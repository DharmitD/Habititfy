# Habitify - AI-Powered Habit Tracker

## Overview

**Habitify** is a Python-based habit tracker and motivational assistant. It helps users log habits, track progress, and receive AI-powered motivational tips to stay consistent. The project leverages **Hugging Face GPT-2** models for generating personalized habit tips.

---

## Features

1\. **Habit Tracking:**

   - Log daily habits with status (e.g., "Completed", "Skipped").

   - View a history of all logged habits.

   - Delete specific habits from the logs.

2\. **Motivational Tips:**

   - Generate actionable, positive motivational tips for specific habits using GPT-2.

3\. **CLI Tool:**

   - A simple Command-Line Interface (CLI) for logging habits, viewing history, and receiving motivational tips.

---

## Setup and Installation

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd habitify
   ```

1.  **Set Up Python Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Install Dependencies:**

    ```bash
    pip install transformers click
    ```

3.  **Download GPT-2 Model:** The GPT-2 model will automatically download the first time you run the CLI tool.

* * * * *

Usage
-----

1.  **Log a Habit:**

    ```bash
    python cli/cli_tool.py log "Exercise" --status "Completed"
    ```

2.  **View Habit History:**

    ```bash
    python cli/cli_tool.py view
    ```

3.  **Get a Motivational Tip:**

    ```bash
    python cli/cli_tool.py motivate "Exercise"
    ```

* * * * *

Future Improvements
-------------------

-   **Add Visualization:** Graphs to display streaks and progress over time.
-   **Trend Analysis:** Use LLMs to identify habit trends and provide feedback.
-   **Mobile Integration:** Extend functionality to mobile apps.

* * * * *

License
-------

This project is open-source and free to use.

