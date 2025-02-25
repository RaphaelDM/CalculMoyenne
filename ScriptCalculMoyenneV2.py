import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from PIL import Image
import os
import sys

mode_theme = "dark"
def changer_theme():
    """Changer le thème entre clair et sombre."""
    global mode_theme, canvas
    mode_actuel = ctk.get_appearance_mode()
    print(f"Mode actuel avant changement : {mode_actuel}")
    if mode_theme == "dark":
        ctk.set_appearance_mode("light")
        bouton_theme.configure(image=soleil_icon, fg_color="#e7e7e7", hover_color="#f6f6f6")  # Changer l'icône en Soleil
        canvas.configure(bg="#FFFFFF")  # En mode clair
        scrollable_frame.configure(fg_color="#FFFFFF",bg_color="#FFFFFF") # En mode
        print("Changement vers le mode clair")
        mode_theme = "light"  # Mettre à jour le mode
    else:
        ctk.set_appearance_mode("dark")
        bouton_theme.configure(image=lune_icon, fg_color="#2A2D2F", hover_color="#3D4346")  # Changer l'icône en Lune
        canvas.configure(bg="#212121")  # En mode sombre
        scrollable_frame.configure(fg_color="#212121",bg_color="#212121") # En mode
        print("Changement vers le mode sombre")
        mode_theme = "dark"  # Mettre à jour le mode

    # Forcer le redessin du bouton après modification
    bouton_theme.update_idletasks()  # Cela s'assure que l'interface est mise à jour après le changement d'icône.
    mode_actuel_apres = ctk.get_appearance_mode()
  


def generer_suggestions(labels, notes, coeffs, moyenne_cible, somme_notes_connues, somme_coeffs, coeff_inconnu, note_inconnue):
    increment = 0.01
    suggestions = []
    suggestion_id = 1
    # Simple adjustments for i in range(len(notes)):
    for i in range(len(notes)):
        note_orig = notes[i]
        while notes[i] <= 20:
            nouvelle_moyenne = (somme_notes_connues + (notes[i] - note_orig) * coeffs[i]) / somme_coeffs
            if note_inconnue is not None:
                note_inconnue = ((moyenne_cible * somme_coeffs) - somme_notes_connues - (note_orig * coeffs[i]) + (notes[i] * coeffs[i])) / coeff_inconnu
            if nouvelle_moyenne >= moyenne_cible:
                suggestions.append((f"Suggesion {suggestion_id}", f"Augmenter {labels[i]} à {notes[i]:.2f} pour atteindre une nouvelle moyenne de {nouvelle_moyenne:.2f}"))
                suggestion_id += 1
                break
            notes[i] += increment
        notes[i] = note_orig  # Reset note to original value for next iteration

    # Combined adjustments
    combinaisons = [(i, j) for i in range(len(notes)) for j in range(i + 1, len(notes))]
    for (i, j) in combinaisons:
        note_orig_i = notes[i]
        note_orig_j = notes[j]
        while notes[i] <= 20 and notes[j] <= 20:
            nouvelle_moyenne = (somme_notes_connues + (notes[i] - note_orig_i) * coeffs[i] + (notes[j] - note_orig_j) * coeffs[j]) / somme_coeffs
            if note_inconnue is not None:
                note_inconnue = ((moyenne_cible * somme_coeffs) - somme_notes_connues - (note_orig_i * coeffs[i]) - (note_orig_j * coeffs[j]) + (notes[i] * coeffs[i]) + (notes[j] * coeffs[j])) / coeff_inconnu
            if nouvelle_moyenne >= moyenne_cible:
                suggestions.append((f"Suggesion {suggestion_id}", f"Augmenter {labels[i]} à {notes[i]:.2f} et {labels[j]} à {notes[j]:.2f} pour atteindre une nouvelle moyenne de {nouvelle_moyenne:.2f}"))
                suggestion_id += 1
                break
            notes[i] += increment
            notes[j] += increment
        notes[i] = note_orig_i  # Reset note to original value for next iteration
        notes[j] = note_orig_j  # Reset note to original value for next iteration

    return suggestions

def afficher_suggestions(suggestions):
    # Frame pour les en-têtes et la Treeview
    list_frame = ctk.CTkFrame(root, fg_color="#808080", corner_radius=10)
    list_frame.pack(pady=5, fill=tk.BOTH, expand=True)

    # Treeview pour afficher les enregistrements
    tree = ttk.Treeview(list_frame, columns=("ID", "Proposition"), show="headings", height=10)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Définir les en-têtes
    tree.heading("ID", text="ID")
    tree.heading("Proposition", text="Proposition")

    # Définir les colonnes
    tree.column("ID", width=50)
    tree.column("Proposition", width=400)

    # Configure les tags de couleur si nécessaire (exemple: ajout de couleurs)
    tree.tag_configure("highlight", background="#f0f0f0")  # Exemple de couleur de fond claire

    # Ajouter les suggestions au Treeview
    for idx, (sugg_id, sugg_desc) in enumerate(suggestions):
        tree.insert("", "end", values=(sugg_id, sugg_desc), tags=("highlight",))

    # Scrollbar pour la Treeview
    scrollbar = ctk.CTkScrollbar(list_frame, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

def reset():
    global table_frame, canvas, scrollbar

    # Réinitialiser le texte de résultat
    result_text.set("")

    # Supprimer tous les widgets enfants du root (y compris la Treeview et tout autre widget)
    try:
        for widget in root.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if child.winfo_exists():
                        child.destroy()
                if widget.winfo_exists():
                    widget.destroy()
    except Exception as e:
        print(f"Erreur lors de la destruction des widgets : {e}")

    # Réinitialiser les éléments dans le Treeview
    global tree
    if 'tree' in globals() and tree.winfo_exists():
        for item in tree.get_children():
            tree.delete(item)

    # Réinitialiser tous les champs de saisie (par exemple, la moyenne cible et les matières)
    try:
        entry_moyenne.delete(0, tk.END)
    except Exception as e:
        print(f"Erreur lors de la réinitialisation des champs de saisie : {e}")

    # Réinitialiser les matières dans le tableau (table_rows)
    try:
        for row in table_rows:
            if row["nom"].winfo_exists():
                row["nom"].delete(0, tk.END)
            if row["note"].winfo_exists():
                row["note"].delete(0, tk.END)
            if row["coeff"].winfo_exists():
                row["coeff"].delete(0, tk.END)
    except Exception as e:
        print(f"Erreur lors de la réinitialisation des matières : {e}")

    # Vider la liste des lignes de matières
    table_rows.clear()

    # Recréer le cadre pour les matières avec scrollbar
    container = ctk.CTkFrame(root)
    container.pack(pady=5, fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container, bg="#212121")
    scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#212121")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    ctk.CTkLabel(scrollable_frame, text="Matière").grid(row=0, column=0, padx=5)
    ctk.CTkLabel(scrollable_frame, text="Note").grid(row=0, column=1, padx=5)
    ctk.CTkLabel(scrollable_frame, text="Coefficient").grid(row=0, column=2, padx=5)

    table_frame = scrollable_frame


def calculer_inconnu():
    try:
        moyenne_cible = float(entry_moyenne.get())
        notes = []
        coeffs = []
        labels = []
        note_inconnue_label = "Inconnue"
        coeff_inconnu = 0
        note_inconnue = None
        for row in table_rows:
            label_text = row["nom"].get()  # Nom complet de la matière
            coeff_val = row["coeff"].get()  # Coefficient de la matière
            note_val = row["note"].get()  # Note de la matière
            try:
                # Essayer de convertir le coefficient en float, avec gestion de la virgule
                coeff_val = float(coeff_val.replace(',', '.'))  # Remplace la virgule par un point si nécessaire
            except ValueError:
                messagebox.showerror("Erreur", "Le coefficient doit être un nombre valide.")
                return
                
            if note_val == "":
                coeff_inconnu = coeff_val
                note_inconnue_label = label_text
            else:
                try:
                    note_val = float(note_val)
                    notes.append(note_val * coeff_val)
                    coeffs.append(coeff_val)
                    labels.append((label_text, note_val, coeff_val))  # Ajouter le nom complet
                except ValueError:
                    messagebox.showerror("Erreur", "Veuillez entrer une note valide.")
                    return

        somme_notes_connues = sum(notes)
        somme_coeffs = sum(coeffs) + coeff_inconnu
        if coeff_inconnu > 0:
            note_inconnue = ((moyenne_cible * somme_coeffs) - somme_notes_connues) / coeff_inconnu
            labels.append((note_inconnue_label, note_inconnue, coeff_inconnu))
        else:
            note_inconnue = None

        # Vérification de la structure de labels après ajout
        print("Labels complets : ", labels)

        if note_inconnue is not None and note_inconnue < 10:
            result_text.set(result_text.get() + f"\n\n Pour obtenir une moyenne de {moyenne_cible}, la note inconnue doit être : {note_inconnue:.2f} Tranquile")
        elif note_inconnue is not None and note_inconnue >= 10 and note_inconnue < 14:
            result_text.set(result_text.get() + f"\n\n Pour obtenir une moyenne de {moyenne_cible}, la note inconnue doit être : {note_inconnue:.2f} C'est fesable ")
        elif note_inconnue is not None and note_inconnue >= 14 and note_inconnue < 20:
            result_text.set(result_text.get() + f"\n\n Pour obtenir une moyenne de {moyenne_cible}, la note inconnue doit être : {note_inconnue:.2f} C'est très chaud")
        elif note_inconnue is not None and note_inconnue > 20:
            result_text.set(result_text.get() + f"\n\n Pour obtenir une moyenne de {moyenne_cible}, la note inconnue doit être : {note_inconnue:.2f} C'est mort cherche pas ")

        if note_inconnue is None:
            print(labels[0][0])  # Vérifie la première matière dans labels

        suggestions = generer_suggestions(
            [label[0] for label in labels],
            [label[1] for label in labels],
            [label[2] for label in labels],
            moyenne_cible,
            somme_notes_connues,
            somme_coeffs,
            coeff_inconnu,
            note_inconnue
        )
        afficher_suggestions(suggestions)  # Affiche le tableau des suggestions
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer une moyenne cible valide.")


def ajouter_matiere():
    row = {}
    row["nom"] = ctk.CTkEntry(table_frame, placeholder_text="Nom de la matière", width=120)
    row["nom"].grid(row=len(table_rows) + 1, column=0, padx=5, pady=2)
    row["note"] = ctk.CTkEntry(table_frame, placeholder_text="Note", width=80)
    row["note"].grid(row=len(table_rows) + 1, column=1, padx=5, pady=2)
    row["coeff"] = ctk.CTkEntry(table_frame, placeholder_text="Coefficient", width=80)
    row["coeff"].grid(row=len(table_rows) + 1, column=2, padx=5, pady=2)

    # Ajout du bouton Supprimer pour chaque ligne
    row["supprimer"] = ctk.CTkButton(table_frame, text="Supprimer", command=lambda row=row: supprimer_matiere(row),fg_color="red")
    row["supprimer"].grid(row=len(table_rows) + 1, column=3, padx=5, pady=2)

    table_rows.append(row)

def supprimer_matiere(row):
    """Supprime la ligne de la matière dans le tableau."""
    row["nom"].destroy()
    row["note"].destroy()
    row["coeff"].destroy()
    row["supprimer"].destroy()
    table_rows.remove(row)

def main_ui():
    global entry_moyenne, table_rows, result_text, suggestions_result, root, table_frame, ctktext, lune_icon, soleil_icon,canvas,bouton_theme,scrollable_frame
    table_rows = []
    root = ctk.CTk()
    root.title("Calcul de note inconnue")
    
    def get_resource_path(relative_path):
        """ Obtenir le chemin absolu pour les ressources. """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    lune_image =Image.open(get_resource_path("assets/soleil.png"))
    soleil_image =Image.open(get_resource_path("assets/lune.png")) 

    # Créer des icônes CTkImage à partir des images Pillow
    lune_icon = ctk.CTkImage(light_image=lune_image, dark_image=lune_image)  # Utiliser la même image pour les modes clair et sombre
    soleil_icon = ctk.CTkImage(light_image=soleil_image, dark_image=soleil_image)  # Utiliser la même image pour les modes clair et sombre

    # Créer un bouton pour changer de thème en haut à droite
    bouton_theme = ctk.CTkButton(root, image=lune_icon, command=changer_theme, fg_color="#2A2D2F", hover_color="#3D4346",text="",width=40,height=40)  # Utiliser une couleur solide
    bouton_theme.place(x=440, y=10)  # Positionner en haut à droite

    # Autres éléments de l'interface
    ctk.CTkLabel(root, text="Moyenne cible :").pack()
    entry_moyenne = ctk.CTkEntry(root)
    entry_moyenne.pack(pady=5)

    ctk.CTkButton(root, text="Ajouter une matière", command=ajouter_matiere).pack(pady=5)
    ctk.CTkButton(root, text="Calculer", command=calculer_inconnu).pack(pady=5)
    ctk.CTkButton(root, text="Réinitialiser", command=reset).pack(pady=5)

    ctk.CTkLabel(root, text="Ajoutez vos matières avec leurs notes et coefficients. Laissez la note vide pour l'inconnue.").pack(pady=5)

    # Ajout du tableau avec une scrollbar
    container = ctk.CTkFrame(root)
    container.pack(pady=5, fill=tk.BOTH, expand=True)

    canvas = ctk.CTkCanvas(container, bg="#212121")
    scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#212121")  # Change the background color of the frame

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    ctk.CTkLabel(scrollable_frame, text="Matière").grid(row=0, column=0, padx=5)
    ctk.CTkLabel(scrollable_frame, text="Note").grid(row=0, column=1, padx=5)
    ctk.CTkLabel(scrollable_frame, text="Coefficient").grid(row=0, column=2, padx=5)

    table_frame = scrollable_frame

    result_text = ctk.StringVar()
    ctk.CTkLabel(root, textvariable=result_text, justify=ctk.LEFT).pack(pady=5)

    root.mainloop()

main_ui()