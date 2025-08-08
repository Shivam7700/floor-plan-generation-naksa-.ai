import tkinter as tk
import math
from tkinter import Button, Text, Frame, Label
from PIL import Image, ImageDraw, ImageTk
from predict import predict_prepare
from functools import partial
from prompt2json import prompt2json, updatePrompt
from openai import OpenAI
import json

# It's good practice to handle potential file errors for configuration
try:
    with open("api_info.json") as f:
        api_info = json.load(f)
except FileNotFoundError:
    print("Error: api_info.json not found. Please create this file with your API key and base URL.")
    exit()

client = OpenAI(
    api_key=api_info.get("api_key"),
    base_url=api_info.get("base_url"),
)


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vastu Floor Plan Generator")

        # --- Top Frame for Controls ---
        top_frame = Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        try:
            pil_image = Image.open("label.png")
            resized_image = pil_image.resize((400, 100), Image.Resampling.LANCZOS)
            self.label_image = ImageTk.PhotoImage(resized_image)
            image_label = Label(top_frame, image=self.label_image)
            image_label.pack(side=tk.TOP, pady=(0, 10))
        except FileNotFoundError:
            print("Warning: label.png not found. The room label image will not be displayed.")

        # --- Drawing Mode Buttons ---
        self.line_mode_button = Button(top_frame, text="Line", command=self.set_line_mode)
        self.line_mode_button.pack(side=tk.LEFT, padx=5)

        self.rect_mode_button = Button(top_frame, text="Rectangle", command=self.set_rectangle_mode)
        self.rect_mode_button.pack(side=tk.LEFT, padx=5)
        
        undo_button = Button(top_frame, text="Cancel (ctrl-z)", command=self.undo)
        undo_button.pack(side=tk.LEFT, padx=5)

        # --- Action Buttons ---
        self.save_button = Button(top_frame, text="Save", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(side=tk.RIGHT, padx=5)

        self.regenerate_button = Button(top_frame, text="Regenerate", command=partial(self.generate_image, repredict=True), state=tk.DISABLED)
        self.regenerate_button.pack(side=tk.RIGHT, padx=5)

        self.generate_button = Button(top_frame, text="Generate", command=partial(self.generate_image, repredict=False))
        self.generate_button.pack(side=tk.RIGHT, padx=5)

        clear_button = Button(top_frame, text="Clear", command=self.clear_canvas)
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # --- Middle Frame for Canvas ---
        canvas_frame = Frame(root)
        canvas_frame.pack(expand=tk.YES, fill=tk.BOTH)

        self.canvas = tk.Canvas(canvas_frame, bg="white", width=512, height=512)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # --- Explanation Frame ---
        self.explanation_frame = Frame(root, pady=5)
        self.explanation_frame.pack(side=tk.TOP, fill=tk.X, padx=10)
        self.explanation_label = Label(self.explanation_frame, text="Vastu explanation will appear here after generation.", wraplength=500, justify=tk.LEFT, fg="#00008B")
        self.explanation_label.pack(fill=tk.X)

        # --- Bottom Frame for Text Prompt ---
        bottom_frame = Frame(root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
        self.text_input_label = Label(bottom_frame, text="Text Prompt:")
        self.text_input_label.pack(side=tk.LEFT)
        self.text_input = Text(bottom_frame, width=60, height=4)
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # --- Instance Variables for Drawing State ---
        self.draw_mode = "none" # Can be 'none', 'line', or 'rectangle'
        self.line_last_point = None
        self.rect_start_point = None
        self.temp_drawing_item = None
        self.lines = []
        self.image = Image.new("RGB", (512, 512), "white")
        self.image_draw = ImageDraw.Draw(self.image)
        self.tk_image = None
        self.text_history = []
        self.binary_image = None
        self.mid = {}
        self.trainer = predict_prepare()

        # --- Event Bindings ---
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Escape>", self.exit_draw_mode)

    # --- Drawing Mode Management ---
    def set_idle_mode(self):
        self.draw_mode = "none"
        self.line_last_point = None
        self.rect_start_point = None
        if self.temp_drawing_item:
            self.canvas.delete(self.temp_drawing_item)
            self.temp_drawing_item = None
        self.line_mode_button.config(relief=tk.RAISED)
        self.rect_mode_button.config(relief=tk.RAISED)

    def set_line_mode(self):
        self.set_idle_mode()
        self.draw_mode = "line"
        self.line_mode_button.config(relief=tk.SUNKEN)

    def set_rectangle_mode(self):
        self.set_idle_mode()
        self.draw_mode = "rectangle"
        self.rect_mode_button.config(relief=tk.SUNKEN)
        
    def exit_draw_mode(self, event=None):
        self.set_idle_mode()

    # --- Mouse Event Handlers ---
    def on_mouse_down(self, event):
        if self.draw_mode == "line":
            self.handle_line_click(event)
        elif self.draw_mode == "rectangle":
            self.start_rectangle(event)

    def on_mouse_drag(self, event):
        if self.draw_mode == "rectangle":
            self.draw_temp_rectangle(event)

    def on_mouse_up(self, event):
        if self.draw_mode == "rectangle":
            self.finish_rectangle(event)

    # --- Line Drawing Logic ---
    def handle_line_click(self, event):
        if 0 <= event.x < self.canvas.winfo_width() and 0 <= event.y < self.canvas.winfo_height():
            snap_point = self.get_orthogonal_snap_point(event.x, event.y)
            if self.line_last_point:
                self.add_line(self.line_last_point, snap_point)
            self.line_last_point = snap_point

    def get_orthogonal_snap_point(self, x, y):
        if self.line_last_point:
            dx = x - self.line_last_point[0]
            dy = y - self.line_last_point[1]
            if abs(dx) > abs(dy): return (x, self.line_last_point[1])
            else: return (self.line_last_point[0], y)
        return (x, y)

    # --- Rectangle Drawing Logic ---
    def start_rectangle(self, event):
        self.rect_start_point = (event.x, event.y)
        self.temp_drawing_item = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="black", dash=(4, 2)
        )

    def draw_temp_rectangle(self, event):
        if not self.rect_start_point: return
        x0, y0 = self.rect_start_point
        x1, y1 = event.x, event.y
        self.canvas.coords(self.temp_drawing_item, x0, y0, x1, y1)

    def finish_rectangle(self, event):
        if not self.rect_start_point: return
        
        if self.temp_drawing_item:
            self.canvas.delete(self.temp_drawing_item)
            self.temp_drawing_item = None
            
        x0, y0 = self.rect_start_point
        x1, y1 = event.x, event.y
        
        # Define the 4 corners of the rectangle
        p1 = (x0, y0)
        p2 = (x1, y0)
        p3 = (x1, y1)
        p4 = (x0, y1)
        
        # Add the 4 lines that make up the rectangle to the list
        self.add_line(p1, p2)
        self.add_line(p2, p3)
        self.add_line(p3, p4)
        self.add_line(p4, p1)
        
        self.rect_start_point = None

    # --- Universal Drawing and State Functions ---
    def add_line(self, p1, p2):
        self.canvas.create_line(p1, p2, fill="black", width=2)
        self.image_draw.line([p1, p2], fill="black", width=2)
        self.lines.append((p1, p2))

    def undo(self, event=None):
        if not self.lines: return
        # A rectangle adds 4 lines, so we undo all 4 if the last action was a rectangle.
        # This is a simplification; a more complex undo stack would be needed for perfect multi-undo.
        num_to_undo = 4 if len(self.lines) >= 4 and self.lines[-1][1] == self.lines[-4][0] else 1
        for _ in range(num_to_undo):
            if self.lines:
                self.lines.pop()
        self.line_last_point = self.lines[-1][1] if self.lines else None
        self.redraw_canvas()

    def redraw_canvas(self):
        canvas_width = self.canvas.winfo_width() or 512
        canvas_height = self.canvas.winfo_height() or 512
        self.canvas.delete("all")
        self.image = Image.new("RGB", (canvas_width, canvas_height), "white")
        self.image_draw = ImageDraw.Draw(self.image)
        for p1, p2 in self.lines:
            self.canvas.create_line(p1, p2, fill="black", width=2)
            self.image_draw.line([p1, p2], fill="black", width=2)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.lines = []
        self.image = Image.new("RGB", (512, 512), "white")
        self.image_draw = ImageDraw.Draw(self.image)
        self.text_input.delete(1.0, tk.END)
        self.explanation_label.config(text="Vastu explanation will appear here after generation.")
        self.set_idle_mode()
        self.binary_image = None
        self.generate_button.config(text="Generate")
        self.regenerate_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.mid = {}
        self.text_history = []

    # --- Core Application Logic (Backend Interaction) ---
    def get_binary(self):
        if not self.lines or len(self.lines) < 3:
            self.explanation_label.config(text="Error: Please draw a closed outline for the house first.")
            return False
        
        self.redraw_canvas()
        if len(self.lines) > 1:
            self.image_draw.line(self.lines[-1][1] + self.lines[0][0], fill="black", width=2)

        fill_image = self.image.copy()
        
        try:
            polygon_points = [p for line in self.lines for p in line]
            min_x = min(p[0] for p in polygon_points); max_x = max(p[0] for p in polygon_points)
            min_y = min(p[1] for p in polygon_points); max_y = max(p[1] for p in polygon_points)
            center_x = int((min_x + max_x) / 2); center_y = int((min_y + max_y) / 2)
            ImageDraw.floodfill(fill_image, xy=(center_x, center_y), value=(0, 0, 0))
        except (ValueError, IndexError) as e:
            print(f"Could not flood fill the outline. Is it closed? Error: {e}")
            self.explanation_label.config(text="Error: The outline must be a single closed shape.")
            return False

        gray_image = fill_image.convert("L")
        binary_image = gray_image.point(lambda x: 0 if x < 128 else 255, "1")
        self.binary_image = binary_image.resize((64, 64), Image.Resampling.NEAREST)
        return True

    def generate_image(self, repredict=False):
        text = self.text_input.get("1.0", "end-1c").strip()
        
        if self.binary_image is None:
            if not self.get_binary(): return
        mask = self.binary_image
        mask.save("mask.png")

        if not text:
            self.explanation_label.config(text="Error: Please provide a description to generate a floor plan.")
            return

        self.explanation_label.config(text="Generating... Please wait.")
        self.root.update_idletasks()

        try:
            if repredict:
                self.text_history = []
                new_text, self.mid, vastu_explanation = prompt2json(text, client=client, model=api_info["model"])
            else:
                if self.generate_button.cget("text") == "Generate":
                    new_text, self.mid, vastu_explanation = prompt2json(text, client=client, model=api_info["model"])
                elif self.generate_button.cget("text") == "Edit":
                    new_text, self.mid, vastu_explanation = updatePrompt(
                        original_json_str=json.dumps(self.mid), new_description=text,
                        client=client, model=api_info["model"],
                    )
        except Exception as e:
            print(f"An error occurred during API call: {e}")
            self.explanation_label.config(text=f"Error communicating with the AI model. Check console.")
            return
            
        self.explanation_label.config(text=vastu_explanation)
        
        if not self.mid or "rooms" not in self.mid or not self.mid["rooms"]:
            error_msg = "Failed to generate a valid floor plan from AI response. Please try a different prompt."
            print(f"Aborting: Invalid or empty floor plan data received: {self.mid}")
            self.explanation_label.config(text=error_msg)
            return

        with open("new_text.json", "w", encoding='utf-8') as f:
            f.write(new_text)
        self.text_history.append(new_text)

        print("Generating floor plan image...")
        prediction = self.trainer.predict(mask, new_text, repredict=repredict)
        
        self.canvas.delete("all")
        self.lines = []
        self.text_input.delete(1.0, tk.END)

        display_size = (self.canvas.winfo_width(), self.canvas.winfo_height())
        self.image = prediction.resize(display_size, Image.Resampling.NEAREST)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)
        
        self.set_idle_mode()
        self.generate_button.config(text="Edit")
        self.regenerate_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        print("Generation complete.")

    def save_image(self):
        if self.tk_image:
            self.image.save("vastu_floor_plan.png")
            print("Image saved as vastu_floor_plan.png")
        else:
            print("No image to save.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()