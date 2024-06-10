import tkinter as tk
from tkinter import ttk, Entry, Label
import sqlite3
import tkinter.messagebox
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import PhotoImage, Label

# Δημιουργία βάσης δεδομένων
def create_tables():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    # Δημιουργία πίνακα recipes
    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                 (id INTEGER PRIMARY KEY,
                 name TEXT UNIQUE NOT NULL,
                 category TEXT NOT NULL,
                 difficulty TEXT NOT NULL,
                 total_time INTEGER NOT NULL)''')

    # Δημιουργία πίνακα ingredients
    c.execute('''CREATE TABLE IF NOT EXISTS ingredients
                 (id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL,
                 recipe_id INTEGER NOT NULL,
                 FOREIGN KEY (recipe_id) REFERENCES recipes(id))''')

    # Δημιουργία πίνακα steps
    c.execute('''CREATE TABLE IF NOT EXISTS steps
                 (id INTEGER PRIMARY KEY,
                 title TEXT NOT NULL,
                 description TEXT NOT NULL,
                 ingredients TEXT NOT NULL,
                 duration INTEGER NOT NULL,
                 recipe_id INTEGER NOT NULL,
                 step_number INTEGER NOT NULL,
                 FOREIGN KEY (recipe_id) REFERENCES recipes(id))''')
    conn.commit()
    conn.close()

# Δημιουργία παραθύρου
root = tk.Tk()
root.title("Συνταγογράφος")
root.geometry("1920x1080")

# Επιλογή δημιουργίας ή αναζήτηση συνταγής
def select_function(function):
    if function == "Δημιουργία Νέας Συνταγής":
        create_recipe_window()
    elif function == "Αναζήτηση Συνταγής":
        search_recipe_window()

# Φόρτωση της φωτογραφίας
image_path = "mageiriki3.jpg"
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Δημιουργία ετικέτας για την εικόνα και τοποθέτηση στο κέντρο του παραθύρου
label = tk.Label(root, image=photo)
label.place(relx=0.5, rely=0.5, anchor="center")

# Δημιουργία βάσης δεδομένων κατά την εκκίνηση
create_tables()

# Ετικέτες για τις διαθέσιμες λειτουργίες
function_label = tk.Label(root, text="Επιλέξτε μια λειτουργία:")
function_label.pack(pady=5)

functions = ["Δημιουργία Νέας Συνταγής", "Αναζήτηση Συνταγής"]
for function in functions:
    button = tk.Button(root, text=function, command=lambda f=function: select_function(f), bg="lightpink")
    button.pack(side="top", fill="x", pady=5)

def create_recipe_window():
    # Δημιουργία παραθύρου για το συνταγογράφου
    recipe_window = tk.Toplevel(root)
    recipe_window.title("Δημιουργία Συνταγής")
    recipe_window.transient(root)
    recipe_window.grab_set()

    # Σύνδεση με τη βάση δεδομένων
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    def on_closing():
        recipe_window.destroy()

    recipe_window.protocol("WM_DELETE_WINDOW", on_closing)

    def submit_recipe():
        changes_made = False  # Flag για να ελέγχουμε αν έχουν γίνει αλλαγές

        try:
            total_time = time_entry.get()
            if not total_time.isdigit():
                raise ValueError("Ο συνολικός χρόνος πρέπει να είναι αριθμητικός.")

            total_time = int(total_time)

            steps_duration = sum([int(entry[3].get()) for entry in step_entries])
            if not str(steps_duration).isdigit():
                raise ValueError("Η διάρκεια των βημάτων πρέπει να είναι αριθμητική.")

            steps_duration = int(steps_duration)

            if total_time != steps_duration:
                raise ValueError("Το άθροισμα της διάρκειας των βημάτων δεν είναι ίσο με τον συνολικό χρόνο.")

            changes_made = True  # Οι αλλαγές έχουν γίνει με επιτυχία

            # Προσθήκη εγγραφής / recipes
            c.execute("INSERT INTO recipes (name, category, difficulty, total_time) VALUES (?, ?, ?, ?)",
                      (recipe_name_entry.get(), category_entry.get(), difficulty_entry.get(), time_entry.get()))
            recipe_id = c.lastrowid  #   ID της νέας συνταγής

            # Προσθήκη εγγραφής / ingredients
            for entry in ingredient_entries:
                ingredient_name = entry.get()
                if ingredient_name:
                    c.execute("INSERT INTO ingredients (name, recipe_id) VALUES (?, ?)", (ingredient_name, recipe_id))

            # Προσθήκη εγγραφής / steps
            for i in range(len(step_entries)):
                title = step_entries[i][0].get()
                if title:  # ο τίτλος του βήματος έχει συμπληρωθεί?
                    description = step_entries[i][1].get()
                    ingredients = step_entries[i][2].get()
                    duration = step_entries[i][3].get()
                    c.execute(
                        "INSERT INTO steps (title, description, ingredients, duration, recipe_id, step_number) VALUES (?, ?, ?, ?, ?, ?)",
                        (title, description, ingredients, duration, recipe_id, i + 1))

            conn.commit()

            # Κλείσιμο του παραθύρου μετά την επιτυχή αποθήκευση
            recipe_window.destroy()
            tkinter.messagebox.showinfo("Επιτυχία", "Η συνταγή αποθηκεύτηκε με επιτυχία!")

        except ValueError as ve:
            if changes_made and conn:
                conn.rollback()
            tkinter.messagebox.showerror("Σφάλμα", str(ve), parent=recipe_window)

        except Exception as e:
            if changes_made and conn:
                conn.rollback()
            tkinter.messagebox.showerror("Σφάλμα", f"Αποτυχία αποθήκευσης της συνταγής: {str(e)}", parent=recipe_window)

    # Πλαίσιο
    main_frame = ttk.Frame(recipe_window, padding="20")
    main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Ετικέτες και πεδία εισαγωγής για τα στοιχεία της συνταγής
    ttk.Label(main_frame, text="Όνομα Συνταγής:").grid(column=0, row=0, sticky=tk.W)
    recipe_name_entry = ttk.Entry(main_frame, width=30)
    recipe_name_entry.grid(column=1, row=0, sticky=tk.W)

    ttk.Label(main_frame, text="Κατηγορία:").grid(column=0, row=1, sticky=tk.W)
    category_entry = ttk.Entry(main_frame, width=30)
    category_entry.grid(column=1, row=1, sticky=tk.W)

    ttk.Label(main_frame, text="Δυσκολία:").grid(column=0, row=2, sticky=tk.W)
    difficulty_entry = ttk.Combobox(main_frame, values=["Εύκολο", "Μεσαίο", "Δύσκολο"])
    difficulty_entry.grid(column=1, row=2, sticky=tk.W)

    ttk.Label(main_frame, text="Συνολικός Χρόνος (λεπτά):").grid(column=0, row=3, sticky=tk.W)
    time_entry = ttk.Entry(main_frame, width=10)
    time_entry.grid(column=1, row=3, sticky=tk.W)

    # Κουμπί υποβολής
    submit_button = ttk.Button(main_frame, text="Υποβολή", command=submit_recipe)
    submit_button.grid(column=0, row=4, columnspan=2, pady=10)

    # frame για τα υλικά
    ingredient_frame = ttk.LabelFrame(recipe_window, text="Υλικά")
    ingredient_frame.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)

    # Λίστες για τα υλικά και τα βήματα
    ingredient_entries = []
    step_entries = []

    steps_frame = ttk.LabelFrame(recipe_window, text="Βήματα")
    steps_frame.grid(column=0, row=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)

    def add_ingredient_entry():
        index = len(ingredient_entries) + 1
        new_label = ttk.Label(ingredient_frame, text=f"Υλικό {index}:")
        new_label.grid(column=0, row=len(ingredient_entries), sticky=tk.W)

        new_entry = ttk.Entry(ingredient_frame, width=30)
        new_entry.grid(column=1, row=len(ingredient_entries), sticky=tk.W)

        ingredient_entries.append(new_entry)

    add_ingredient_button = ttk.Button(recipe_window, text="Προσθήκη Υλικού", command=add_ingredient_entry)
    add_ingredient_button.grid(column=1, row=1, padx=10, pady=10)

    # Κουμπί προσθήκης βήματος
    def add_step_entry():
        step_number = len(step_entries) + 1  #  αριθμός βήματος

        ttk.Label(steps_frame, text=f"Βήμα {step_number}").grid(column=0, row=step_number - 1, sticky=tk.W)

        new_title_entry = ttk.Entry(steps_frame, width=30)
        new_title_entry.grid(column=1, row=step_number - 1, sticky=tk.W)

        ttk.Label(steps_frame, text="Περιγραφή:").grid(column=2, row=step_number - 1, sticky=tk.W)
        new_description_entry = ttk.Entry(steps_frame, width=50)
        new_description_entry.grid(column=3, row=step_number - 1, sticky=tk.W)

        ttk.Label(steps_frame, text="Υλικά:").grid(column=4, row=step_number - 1, sticky=tk.W)
        new_ingredients_entry = ttk.Entry(steps_frame, width=30)
        new_ingredients_entry.grid(column=5, row=step_number - 1, sticky=tk.W)

        ttk.Label(steps_frame, text="Διάρκεια (λεπτά):").grid(column=6, row=step_number - 1, sticky=tk.W)
        new_duration_entry = ttk.Entry(steps_frame, width=10)
        new_duration_entry.grid(column=7, row=step_number - 1, sticky=tk.W)

        step_entries.append((new_title_entry, new_description_entry, new_ingredients_entry, new_duration_entry))

    add_step_button = ttk.Button(steps_frame, text="Προσθήκη Βήματος", command=add_step_entry)
    add_step_button.grid(column=1, row=30, pady=5)

    # Κέντραρισμός του παραθύρου
    window_width = 1200
    window_height = 700

    position_right = int(recipe_window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(recipe_window.winfo_screenheight() / 2 - window_height / 2)

    recipe_window.geometry("{}x{}+{}+{}".format(window_width, window_height, position_right, position_down))


# Αναζήτηση συνταγών
def search_recipe():
    # Καθαρισμός του προηγούμενου αποτελέσματος για να μην αναπαράγονται τα αποτελέσματα συνέχεια
    for widget in result_frame.winfo_children():
        widget.destroy()

    global result_label
    result_label = tk.Label(result_frame, text="")
    result_label.pack()

    # Σύνδεση με τη βάση δεδομένων
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    # Ανάκτηση της αναζήτησης από το πεδίο εισόδου
    search_term = search_entry.get()

    # Αναζήτηση συνταγών με βάση το όνομα ή την κατηγορία
    c.execute("SELECT * FROM recipes WHERE name LIKE ? OR category LIKE ?",
              ('%' + search_term + '%', '%' + search_term + '%'))
    recipes = c.fetchall()

    # Κλείσιμο σύνδεσης με τη βάση δεδομένων
    conn.close()

    if not recipes:
        result_label.config(text="Δεν βρέθηκε καμία συνταγή.")
    else:
        result_label.config(text="")
        for recipe in recipes:
            recipe_id = recipe[0]
            recipe_name = recipe[1]
            recipe_button_frame = tk.Frame(result_frame)
            recipe_button_frame.pack()

            # Εμφάνιση ονόματος συνταγής ως κουμπί
            recipe_name_button = tk.Button(recipe_button_frame, text=recipe_name,
                                           command=lambda id=recipe_id: execute_recipe(id))
            recipe_name_button.pack(side="left")

            # Κουμπί επιλογής για διαγραφή συνταγής
            delete_button = tk.Button(recipe_button_frame, text="Διαγραφή",
                                      command=lambda id=recipe_id: delete_recipe(id))
            delete_button.pack(side="left")

            # Κουμπί επιλογής για τροποποίηση συνταγής
            edit_button = tk.Button(recipe_button_frame, text="Τροποποίηση",
                                    command=lambda id=recipe_id: edit_recipe(id))
            edit_button.pack(side="left")

            # Κουμπί επιλογής για εκτέλεση συνταγής
            execute_button = tk.Button(recipe_button_frame, text="Εκτέλεση",
                                       command=lambda id=recipe_id: execute_recipe(id))
            execute_button.pack(side="left")

            result_label.config(text=result_label.cget("text") + "\n")


# Συνάρτηση για το παράθυρο αναζήτησης συνταγών
def search_recipe_window():
    global search_window
    search_window = tk.Toplevel(root)
    search_window.title("Αναζήτηση Συνταγής")

    def on_close():
        search_window.destroy()

    search_window.protocol("WM_DELETE_WINDOW", on_close)

    # Ετικέτα και πεδίο εισαγωγής για την αναζήτηση
    global search_entry
    tk.Label(search_window, text="Αναζήτηση:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    search_entry = tk.Entry(search_window)
    search_entry.grid(row=0, column=1, padx=10, pady=5)

    # Κουμπί αναζήτησης
    search_button = tk.Button(search_window, text="Αναζήτηση", command=search_recipe)
    search_button.grid(row=0, column=2, padx=10, pady=5)

    # Πλαίσιο για τα αποτελέσματα
    global result_frame
    result_frame = tk.Frame(search_window)
    result_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

    # Αποτελέσματα αναζήτησης
    global result_label
    result_label = tk.Label(result_frame, text="")
    result_label.pack()

    # Κέντραρισμός του παραθύρου
    window_width = search_window.winfo_reqwidth()
    window_height = search_window.winfo_reqheight()
    position_right = int(search_window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(search_window.winfo_screenheight() / 2 - window_height / 2)
    search_window.geometry("+{}+{}".format(position_right, position_down))

# Διαγραφή συνταγής
def delete_recipe(recipe_id):
    try:
        # Σύνδεση με τη βάση δεδομένων
        conn = sqlite3.connect('recipes.db')
        c = conn.cursor()

        # Διαγραφή των υλικών της συγκεκριμένης συνταγής
        c.execute("DELETE FROM ingredients WHERE recipe_id=?", (recipe_id,))

        # Διαγραφή των βημάτων της συγκεκριμένης συνταγής
        c.execute("DELETE FROM steps WHERE recipe_id=?", (recipe_id,))

        # Διαγραφή της συνταγής από τον πίνακα recipes
        c.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))

        conn.commit()
        conn.close()

        # Κλείσιμο παραθύρου αναζήτησης
        search_window.destroy()

        # Εμφάνιση μηνύματος επιβεβαίωσης διαγραφής
        success_window = tk.Toplevel()
        success_window.title("Επιτυχής Διαγραφή")
        success_label = tk.Label(success_window, text=f"Η συνταγή με ID {recipe_id} διαγράφηκε επιτυχώς.")
        success_label.pack()
        ok_button = tk.Button(success_window, text="OK", command=success_window.destroy)
        ok_button.pack()
        edit_window.destroy()


        # Κεντράρισμα του παραθύρου στη μέση της οθόνης
        success_window.update_idletasks()
        width = success_window.winfo_width()
        height = success_window.winfo_height()
        x = (success_window.winfo_screenwidth() // 2) - (width // 2)
        y = (success_window.winfo_screenheight() // 2) - (height // 2)
        success_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    except Exception as e:
        tkinter.messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής της συνταγής: {str(e)}")








def edit_recipe(recipe_id):
    # Κλείσιμο παραθύρου αναζήτησης
    search_window.destroy()
    # Σύνδεση με τη βάση δεδομένων
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    # Επιλογή της συνταγής με βάση το recipe_id
    c.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,))
    recipe = c.fetchone()

    if not recipe:
        messagebox.showerror("Σφάλμα", f"Η συνταγή με ID {recipe_id} δεν βρέθηκε.")
        conn.close()
        return

    # Δημιουργία παραθύρου επεξεργασίας
    global edit_window
    edit_window = tk.Toplevel()
    edit_window.title("Επεξεργασία Συνταγής")

    # Ετικέτες και πεδία εισαγωγής για τα στοιχεία της συνταγής
    ttk.Label(edit_window, text="Όνομα Συνταγής:").grid(column=0, row=0, sticky=tk.W)
    edit_recipe_name_entry = ttk.Entry(edit_window, width=30)
    edit_recipe_name_entry.grid(column=1, row=0, sticky=tk.W)
    edit_recipe_name_entry.insert(0, recipe[1])  # Εισαγωγή του τρέχοντος ονόματος της συνταγής

    ttk.Label(edit_window, text="Κατηγορία:").grid(column=0, row=1, sticky=tk.W)
    edit_category_entry = ttk.Entry(edit_window, width=30)
    edit_category_entry.grid(column=1, row=1, sticky=tk.W)
    edit_category_entry.insert(0, recipe[2])  # Εισαγωγή της τρέχουσας κατηγορίας της συνταγής

    ttk.Label(edit_window, text="Δυσκολία:").grid(column=0, row=2, sticky=tk.W)
    edit_difficulty_entry = ttk.Combobox(edit_window, values=["Εύκολο", "Μεσαίο", "Δύσκολο"])
    edit_difficulty_entry.grid(column=1, row=2, sticky=tk.W)
    edit_difficulty_entry.set(recipe[3])  # Επιλογή της τρέχουσας δυσκολίας της συνταγής

    ttk.Label(edit_window, text="Συνολικός Χρόνος (λεπτά):").grid(column=0, row=3, sticky=tk.W)
    edit_time_entry = ttk.Entry(edit_window, width=10)
    edit_time_entry.grid(column=1, row=3, sticky=tk.W)
    edit_time_entry.insert(0, recipe[4])  # Εισαγωγή του τρέχοντος συνολικού χρόνου της συνταγής

    # Κουμπί επιβεβαίωσης τροποποίησης
    def confirm_edit():
        try:
            # Σύνδεση με τη βάση δεδομένων
            conn = sqlite3.connect('recipes.db')
            c = conn.cursor()

            # Έλεγχος του συνολικού χρόνου και της συνολικής διάρκειας των βημάτων
            total_time = int(edit_time_entry.get())
            steps_total_duration = sum(int(entry[3].get()) for entry in step_entries)

            if total_time != steps_total_duration:
                raise ValueError("Ο συνολικός χρόνος δεν είναι ίσος με τη συνολική διάρκεια των βημάτων")

            # Ενημέρωση της εγγραφής στον πίνακα recipes
            c.execute("UPDATE recipes SET name=?, category=?, difficulty=?, total_time=? WHERE id=?",
                      (edit_recipe_name_entry.get(), edit_category_entry.get(), edit_difficulty_entry.get(),
                       edit_time_entry.get(), recipe_id))

            # Εφόσον υπάρχουν πεδία εισαγωγής για τα υλικά, εκτέλεσε αυτή την ενέργεια
            if ingredient_entries:
                # Προετοιμασία για ενημέρωση του πίνακα ingredients
                c.execute("DELETE FROM ingredients WHERE recipe_id=?", (recipe_id,))
                for entry in ingredient_entries:
                    ingredient_name = entry.get()
                    if ingredient_name:
                        c.execute("INSERT INTO ingredients (name, recipe_id) VALUES (?, ?)",
                                  (ingredient_name, recipe_id))

            # Εφόσον υπάρχουν πεδία εισαγωγής για τα βήματα, εκτέλεσε αυτή την ενέργεια
            if step_entries:
                # Προετοιμασία για ενημέρωση του πίνακα steps
                c.execute("DELETE FROM steps WHERE recipe_id=?", (recipe_id,))
                for i in range(len(step_entries)):
                    title = step_entries[i][0].get()
                    if title:
                        description = step_entries[i][1].get()
                        ingredients = step_entries[i][2].get()
                        duration = step_entries[i][3].get()
                        c.execute(
                            "INSERT INTO steps (title, description, ingredients, duration, recipe_id, step_number) VALUES (?, ?, ?, ?, ?, ?)",
                            (title, description, ingredients, duration, recipe_id, i + 1))

            conn.commit()
            messagebox.showinfo("Επιτυχία", "Η συνταγή ενημερώθηκε επιτυχώς!")
            edit_window.destroy()
        except Exception as e:
            conn.rollback()  # Αν υπάρξει σφάλμα, ανατρέπουμε τις αλλαγές
            messagebox.showerror("Σφάλμα", f"Αποτυχία ενημέρωσης της συνταγής: {str(e)}", parent=edit_window)
        finally:
            # Κλείσιμο σύνδεσης με τη βάση δεδομένων
            conn.close()

    confirm_button = ttk.Button(edit_window, text="Επιβεβαίωση", command=confirm_edit)
    confirm_button.grid(column=0, row=4, columnspan=2, pady=10)

    # Κουμπί διαγραφής συνταγής
    delete_button = ttk.Button(edit_window, text="Διαγραφή Συνταγής", command=lambda: delete_recipe(recipe_id))
    delete_button.grid(column=0, row=5, columnspan=2, pady=5)

    # frame για τα υλικά
    ingredient_frame = ttk.LabelFrame(edit_window, text="Υλικά")
    ingredient_frame.grid(column=0, row=6, columnspan=2, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    # frame για τα βήματα
    steps_frame = ttk.LabelFrame(edit_window, text="Βήματα")
    steps_frame.grid(column=0, row=7, columnspan=2, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Εκτέλεση της SQL εντολής για την ανάκτηση των υλικών και των βημάτων της συνταγής
    c.execute("SELECT * FROM ingredients WHERE recipe_id=?", (recipe_id,))
    ingredients = c.fetchall()

    c.execute("SELECT * FROM steps WHERE recipe_id=? ORDER BY step_number", (recipe_id,))
    steps = c.fetchall()

    def delete_step(index):
        # Διαγραφή των widgets του σχετικού βήματος
        for widget in steps_frame.grid_slaves():
            if int(widget.grid_info()["row"]) == index:
                widget.grid_forget()
        # Αφαίρεση του βήματος από τη λίστα step_entries
        del step_entries[index]

    def add_ingredient():
        idx = len(ingredient_entries)  # Αριθμός του νέου υλικού
        ttk.Label(ingredient_frame, text=f"Υλικό {idx + 1}:").grid(column=0, row=idx, sticky=tk.W)
        entry = ttk.Entry(ingredient_frame, width=30)
        entry.grid(column=1, row=idx, sticky=tk.W)
        ingredient_entries.append(entry)

        # Κουμπί διαγραφής του συγκεκριμένου υλικού
        delete_button = ttk.Button(ingredient_frame, text="Διαγραφή",
                                   command=lambda index=idx: delete_ingredient(index))
        delete_button.grid(column=2, row=idx, sticky=tk.W)

    def delete_ingredient(index):
        del ingredient_entries[index]  # Διαγραφή του συγκεκριμένου υλικού από τη λίστα
        for widget in ingredient_frame.winfo_children():  # Αφαίρεση όλων των widgets από το πλαίσιο
            widget.grid_forget()
        # Επανασχεδίαση των widgets εισαγωγής υλικών
        for i, entry in enumerate(ingredient_entries):
            ttk.Label(ingredient_frame, text=f"Υλικό {i + 1}:").grid(column=0, row=i, sticky=tk.W)
            entry.grid(column=1, row=i, sticky=tk.W)
            delete_button = ttk.Button(ingredient_frame, text="Διαγραφή", command=lambda idx=i: delete_ingredient(idx))
            delete_button.grid(column=2, row=i, sticky=tk.W)

    def add_step():
        i = len(step_entries)
        ttk.Label(steps_frame, text=f"Βήμα {i + 1}:").grid(column=0, row=i, sticky=tk.W)
        title_entry = ttk.Entry(steps_frame, width=30)
        title_entry.grid(column=1, row=i, sticky=tk.W)

        ttk.Label(steps_frame, text="Περιγραφή:").grid(column=2, row=i, sticky=tk.W)
        description_entry = ttk.Entry(steps_frame, width=50)
        description_entry.grid(column=3, row=i, sticky=tk.W)

        ttk.Label(steps_frame, text="Υλικά:").grid(column=4, row=i, sticky=tk.W)
        ingredients_entry = ttk.Entry(steps_frame, width=30)
        ingredients_entry.grid(column=5, row=i, sticky=tk.W)

        ttk.Label(steps_frame, text="Διάρκεια (ώρες:λεπτά):").grid(column=6, row=i, sticky=tk.W)
        duration_entry = ttk.Entry(steps_frame, width=10)
        duration_entry.grid(column=7, row=i, sticky=tk.W)

        delete_button = ttk.Button(steps_frame, text="Διαγραφή", command=lambda index=i: delete_step(index))
        delete_button.grid(column=8, row=i, sticky=tk.W)

        step_entries.append((title_entry, description_entry, ingredients_entry, duration_entry))

    # Κουμπί προσθήκης υλικού
    add_ingredient_button = ttk.Button(edit_window, text="Προσθήκη Υλικού", command=add_ingredient)
    add_ingredient_button.grid(column=0, row=8, columnspan=2, pady=5)

    # Κουμπί προσθήκης βήματος
    add_step_button = ttk.Button(edit_window, text="Προσθήκη Βήματος", command=add_step)
    add_step_button.grid(column=0, row=9, columnspan=2, pady=5)

    # Πλήθος συνολικών βημάτων
    num_steps = len(steps)

    # Πεδία εισαγωγής για τα υλικά
    ingredient_entries = []

    # Δημιουργία πεδίων εισαγωγής για τα υλικά
    for i, ingredient in enumerate(ingredients):
        ttk.Label(ingredient_frame, text=f"Υλικό {i + 1}:").grid(column=0, row=i, sticky=tk.W)
        entry = ttk.Entry(ingredient_frame, width=30)
        entry.grid(column=1, row=i, sticky=tk.W)
        entry.insert(0, ingredient[1])  # Εισαγωγή του τρέχοντος ονόματος του υλικού
        ingredient_entries.append(entry)

        # Δημιουργία κουμπιού διαγραφής για το συγκεκριμένο υλικό
        delete_button = ttk.Button(ingredient_frame, text="Διαγραφή", command=lambda index=i: delete_ingredient(index))
        delete_button.grid(column=2, row=i, sticky=tk.W)

    # Συνάρτηση για τη διαγραφή ενός υλικού
    def delete_ingredient(index):
        del ingredient_entries[index]  # Διαγραφή του συγκεκριμένου υλικού από τη λίστα
        for widget in ingredient_frame.winfo_children():  # Αφαίρεση όλων των widgets από το πλαίσιο
            widget.grid_forget()
        # Επανασχεδίαση των widgets εισαγωγής υλικών
        for i, entry in enumerate(ingredient_entries):
            ttk.Label(ingredient_frame, text=f"Υλικό {i + 1}:").grid(column=0, row=i, sticky=tk.W)
            entry.grid(column=1, row=i, sticky=tk.W)
            delete_button = ttk.Button(ingredient_frame, text="Διαγραφή", command=lambda idx=i: delete_ingredient(idx))
            delete_button.grid(column=2, row=i, sticky=tk.W)

    # Πεδία εισαγωγής για τα βήματα
    global step_entries
    step_entries = []

    # Δημιουργία πεδίων εισαγωγής για τα βήματα
    for i, step in enumerate(steps):
        ttk.Label(steps_frame, text=f"Βήμα {i + 1}:").grid(column=0, row=i, sticky=tk.W)
        title_entry = ttk.Entry(steps_frame, width=30)
        title_entry.grid(column=1, row=i, sticky=tk.W)
        title_entry.insert(0, step[1])  # Εισαγωγή του τρέχοντος τίτλου του βήματος

        ttk.Label(steps_frame, text="Περιγραφή:").grid(column=2, row=i, sticky=tk.W)
        description_entry = ttk.Entry(steps_frame, width=50)
        description_entry.grid(column=3, row=i, sticky=tk.W)
        description_entry.insert(0, step[2])  # Εισαγωγή της τρέχουσας περιγραφής του βήματος

        ttk.Label(steps_frame, text="Υλικά:").grid(column=4, row=i, sticky=tk.W)
        ingredients_entry = ttk.Entry(steps_frame, width=30)
        ingredients_entry.grid(column=5, row=i, sticky=tk.W)
        ingredients_entry.insert(0, step[3])  # Εισαγωγή των τρεχουσών υλικών του βήματος

        ttk.Label(steps_frame, text="Διάρκεια (ώρες:λεπτά):").grid(column=6, row=i, sticky=tk.W)
        duration_entry = ttk.Entry(steps_frame, width=10)
        duration_entry.grid(column=7, row=i, sticky=tk.W)
        duration_entry.insert(0, step[4])  # Εισαγωγή της τρέχουσας διάρκειας του βήματος

        # Κουμπί διαγραφής βήματος
        delete_button = ttk.Button(steps_frame, text="Διαγραφή", command=lambda index=i: delete_step(index))
        delete_button.grid(column=8, row=i, sticky=tk.W)

        step_entries.append((title_entry, description_entry, ingredients_entry, duration_entry))

    # Αρχική τοποθέτηση του παραθύρου στο κέντρο της οθόνης
    window_width = 1200
    window_height = 800
    screen_width = edit_window.winfo_screenwidth()
    screen_height = edit_window.winfo_screenheight()
    x_coordinate = int((screen_width - window_width) / 2)
    y_coordinate = int((screen_height - window_height) / 2)
    edit_window.geometry(f'{window_width}x{window_height}+{x_coordinate}+{y_coordinate}')
    edit_window.update_idletasks()



# Εκτέλεση συνταγής
def execute_recipe(recipe_id):
    # Κλείσιμο παραθύρου αναζήτησης
    search_window.destroy()

    # Συνάρτηση για ενημέρωση των πληροφοριών του τρέχοντος βήματος
    def update_step_info(step_index):
        if step_index < len(steps):
            step = steps[step_index]
            title_label.config(text=f"Βήμα {step_index + 1}: {step[0]}")
            description_label.config(text=f"Περιγραφή: {step[1]}")
            ingredients_label.config(text=f"Υλικά: {step[2]}")
            duration_label.config(text=f"Διάρκεια: {step[3]}")
            progress_var.set(int((step_index + 1) / len(steps) * 100))
            if step_index == len(steps) - 1:
                next_button.config(text="Ολοκλήρωση")

    # Συνάρτηση για τη μετάβαση στο επόμενο βήμα
    def next_step():
        nonlocal current_step_index
        current_step_index += 1
        if current_step_index == len(steps):
            messagebox.showinfo("Ολοκλήρωση", "Η συνταγή ολοκληρώθηκε επιτυχώς!")
            recipe_window.destroy()
        else:
            update_step_info(current_step_index)

    # Συνδέση με τη βάση δεδομένων
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    # Λήψη των βημάτων και των υλικών της συνταγής από τη βάση δεδομένων
    c.execute("SELECT title, description, ingredients, duration FROM steps WHERE recipe_id=?", (recipe_id,))
    steps = c.fetchall()

    if not steps:
        messagebox.showerror("Σφάλμα", "Δεν βρέθηκαν βήματα για τη συνταγή με ID: " + str(recipe_id))
        return

    # Δημιουργία παραθύρου GUI για την εκτέλεση της συνταγής
    recipe_window = tk.Toplevel()
    recipe_window.title("Εκτέλεση Συνταγής")

    # Ετικέτες για τα υλικά και τα βήματα
    title_label = ttk.Label(recipe_window, text="")
    title_label.pack(anchor=tk.W, padx=10, pady=5)

    description_label = ttk.Label(recipe_window, text="")
    description_label.pack(anchor=tk.W, padx=10, pady=5)

    ingredients_label = ttk.Label(recipe_window, text="")
    ingredients_label.pack(anchor=tk.W, padx=10, pady=5)

    duration_label = ttk.Label(recipe_window, text="")
    duration_label.pack(anchor=tk.W, padx=10, pady=5)

    # Πρόοδος στην εκτέλεση της συνταγής
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(recipe_window, orient=tk.HORIZONTAL, length=200, mode='determinate', variable=progress_var)
    progress_bar.pack(pady=10)

    # Κουμπί για την πρόοδο στο επόμενο βήμα
    next_button = ttk.Button(recipe_window, text="Επόμενο Βήμα", command=next_step)
    next_button.pack(pady=10)

    # Αρχικοποίηση του πρώτου βήματος
    current_step_index = 0
    update_step_info(current_step_index)



    # Αρχική τοποθέτηση του παραθύρου στο κέντρο της οθόνης
    window_width = 500
    window_height = 300
    screen_width = recipe_window.winfo_screenwidth()
    screen_height = recipe_window.winfo_screenheight()
    x_coordinate = int((screen_width - window_width) / 2)
    y_coordinate = int((screen_height - window_height) / 2)
    recipe_window.geometry(f'{window_width}x{window_height}+{x_coordinate}+{y_coordinate}')
    recipe_window.update_idletasks()




root.mainloop()
