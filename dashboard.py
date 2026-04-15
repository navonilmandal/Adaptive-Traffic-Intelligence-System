import matplotlib.pyplot as plt
import collections

# Use a sleek dark theme
plt.style.use('dark_background')

class LiveDashboard:
    def __init__(self):
        plt.ion() # Turn on interactive mode (non-blocking)
        self.fig = plt.figure(figsize=(10, 8))
        self.fig.canvas.manager.set_window_title('Smart Traffic AI Dashboard')

        # --- 1. Speed Line Chart ---
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax1.set_title('Agent Speed (m/s)', color='cyan', pad=10)
        self.ax1.set_ylim(0, 30)
        self.ax1.set_ylabel("Speed")
        self.speed_data = collections.deque(maxlen=150)
        self.time_data = collections.deque(maxlen=150)
        self.line1, = self.ax1.plot([], [], 'c-', linewidth=2)

        # --- 2. Congestion Line Chart ---
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax2.set_title('Local Congestion (Vehicles)', color='magenta', pad=10)
        self.ax2.set_ylim(0, 15)
        self.ax2.set_ylabel("Cars on current road")
        self.density_data = collections.deque(maxlen=150)
        self.line2, = self.ax2.plot([], [], 'm-', linewidth=2)

        # --- 3. Decision Log Text Area ---
        self.ax3 = self.fig.add_subplot(2, 1, 2)
        self.ax3.axis('off') # Hide the grid/axes
        self.ax3.set_title('Live Decision Log', loc='left', color='yellow', fontsize=14)
        
        self.log_texts = collections.deque(maxlen=10) # Keep the last 10 lines
        self.log_texts.append("System Initialized. Waiting for Agent Deployment...")
        
        # The actual text object we will update
        self.text_box = self.ax3.text(0.01, 0.95, "", va='top', ha='left', family='consolas', size=11, color='lime')

        plt.tight_layout()
        self.fig.canvas.draw()
        plt.pause(0.1)

    def update(self, current_time, speed, density, decision_text):
        if not plt.fignum_exists(self.fig.number):
            return # Exit safely if you close the dashboard window

        # Store new data
        self.time_data.append(current_time)
        self.speed_data.append(speed)
        self.density_data.append(density)

        # Scroll the X-axis as time moves forward
        min_x = max(0, current_time - 40)
        max_x = max(40, current_time + 5)
        self.ax1.set_xlim(min_x, max_x)
        self.ax2.set_xlim(min_x, max_x)

        # Update Lines
        self.line1.set_data(self.time_data, self.speed_data)
        self.line2.set_data(self.time_data, self.density_data)

        # Update the Text Log
        if decision_text:
            time_str = f"[{current_time:.1f}s]"
            # Format nicely
            self.log_texts.append(f"{time_str} > {decision_text}")
            
        # Stitch the list of logs together with line breaks
        log_display = "\n\n".join(self.log_texts)
        self.text_box.set_text(log_display)

        # Refresh the canvas cleanly
        try:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except:
            pass