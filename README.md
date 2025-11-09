# Block-Clicker

#### Video Demo:  https://youtu.be/Q2NfPoevKuw

#### Description:

Block-Clicker is a full-stack web application that gamifies the simple act of clicking. It is a persistent, incremental "clicker" game, heavily inspired by classics like *Cookie Clicker* but with a *Minecraft*-inspired aesthetic. Built with a Python and Flask backend, a SQLite database, and a dynamic JavaScript-driven frontend, this project demonstrates a complete, self-contained web application with full user authentication, persistent data storage, and real-time game mechanics.

The core premise is simple: you click a block to earn "blocks". These blocks serve as the in-game currency, which you can then spend on upgrades to increase your earning potential. The game features two primary methods of earning: active clicking (Blocks per Click, or BPC) and passive generation (Blocks per Second, or BPS). This dual-progression system encourages both active play and idle accumulation, creating an addictive and engaging gameplay loop.

-----

## Key Features

### 1\. Full User Authentication & Session Management

The application is built for multiple users, with all progress tied to a secure, persistent account.

  * **User Registration:** New users can create an account via the `/register` route. The system requires a username and a password. To ensure security, the password is not stored in plaintext. Instead, the application uses `werkzeug.security` to generate a secure password hash, which is what is stored in the database. The registration form (`register.html`) includes password confirmation to ensure the user types their password correctly.
  * **User Login:** Registered users can log in via the `/login` route. The application checks their submitted password against the stored hash using `check_password_hash`.
  * **Session Management:** Upon a successful login, the user's unique `id` from the database is stored in the `flask_session`. This session identifies the user as they navigate the site, allowing them to access their own game state and progress. The application is configured to use a filesystem-based session type, ensuring that login status persists.
  * **Logout:** A dedicated `/logout` route clears the session, logging the user out and redirecting them to the home page.

### 2\. Core Gameplay & Persistent Progress

All game progress is saved in real-time to a dedicated SQLite database (`gamers.db`), allowing users to log out and return later to find their progress intact.

  * **Database Schema:** The `gamers.db` file defines two main tables:
      * `users`: Stores user-specific data, including their `id`, `username`, password `hash`, and their current game stats: `blocks` (total currency), `bpc` (blocks per click, defaulting to 1), and `bps` (blocks per second, defaulting to 0).
      * `upgrades`: A separate table that tracks the `level` (defaulting to 0) of each `upgrade_name` for each `user_id`. This relational design keeps the `users` table clean and makes the upgrade system easily extensible.
  * **Active Mining:** The main game interface (`index.html`) features a clickable "stone" block image. Clicking this block triggers the `incrementBlocks()` JavaScript function. This function sends an asynchronous `POST` request to the `/mine` endpoint. The server then increments the user's block count in the database by their current `bpc` value and returns the new total, which JavaScript uses to update the counter on the page instantly.
  * **Passive Mining (Idle Game):** The game respects the player's time by allowing for idle progress. A JavaScript `setInterval` function on the main page calls the `autoMine()` function every 1000 milliseconds (1 second). This function checks the user's current BPS value from a `data-bps` attribute and, if it's greater than zero, sends a `POST` request to the `/auto_mine` endpoint. On the backend, this route adds the user's `bps` stat to their `blocks` total in the database and returns the new total, ensuring that even when the user is just watching the page, their block count automatically increases.

### 3\. Dynamic Upgrade System

The "Upgrades" shop is the primary driver of progression. Users spend their earned blocks to buy items that enhance their earning power.

  * **Three Upgrade Types:** The application defines three distinct upgrades in the `app.py` backend:
    1.  **⛏️ Pickaxe:** A `bpc` upgrade. Each level purchased adds +1 to the user's `bpc` stat, making each click more valuable.
    2.  **🧍‍♂️ Friend:** A low-tier `bps` upgrade. Each level adds +1 to the user's `bps` stat, increasing their passive block generation.
    3.  **🌟 Beacon:** A high-tier `bps` upgrade. It is much more expensive but adds +10 to the user's `bps` stat, providing a significant boost to idle income.
  * **Exponential Cost Scaling:** To ensure balanced progression, upgrades do not have a fixed cost. The cost for the next level of an upgrade is calculated dynamically on both the server (when loading the page and processing a purchase) and the client (after a purchase). The formula is: `current_cost = int(base_cost * (multiplier ** current_level))`. The Pickaxe has a base cost of 10 and a 1.2x multiplier, the Friend has a base cost of 100 and a 1.5x multiplier, and the Beacon has a base cost of 1000 and a 2x multiplier.
  * **Asynchronous Purchasing:** When a user clicks a "Buy" button, the `buyUpgrade(upgradeType)` JavaScript function is called. This sends an asynchronous `POST` request to the `/upgrade` endpoint, sending a JSON object with the `upgrade_type`.
  * **Real-time UI Updates:** The server validates the purchase (checking if the user has enough blocks). If successful, it subtracts the cost, increments the upgrade level, updates the user's BPC/BPS stats in the database, and returns a JSON object with the user's new block total, new BPC, new BPS, the upgrade's new level, and the calculated cost for the *next* level. The JavaScript on the frontend then uses this data to update all relevant parts of the UI (the block counter, BPS display, and the specific upgrade's level and cost) instantly, all without a page reload.

### 4\. Public Leaderboard

To foster a sense of competition, the application features a global leaderboard accessible to all users.

  * The `/leaderboard` route queries the `users` table and retrieves the `username` and `blocks` for all users, sorting them in `DESC` (descending) order by their block count.
  * This list is then passed to the `leaderboard.html` template, which renders a Bootstrap-styled table. The template uses a `loop.index` to display the rank, along with the `user["username"]` and `user["blocks"]` for each person, allowing players to see how they stack up against everyone else.

-----

## Technical Stack

  * **Backend:** **Python** with the **Flask** micro-framework.
  * **Database:** **SQLite** accessed via the **CS50 SQL library**.
  * **Session Management:** **Flask-Session** for persistent, server-side user sessions.
  * **Frontend:**
      * **HTML & Jinja2:** For server-side templating and dynamic page rendering.
      * **CSS:** Custom styling in `styles.css` provides the *Minecraft*-themed background, a two-column layout, and button/text styling.
      * **JavaScript:** Vanilla JavaScript is used extensively for all client-side interactivity. This includes handling click events, making asynchronous `fetch` requests to the Flask backend (for mining and upgrading), and dynamically updating the DOM to reflect changes in the game state without reloading the page.
  * **UI Framework:** **Bootstrap 5.3** is used for responsive navigation bar components and clean, consistent styling of forms, buttons, and tables.