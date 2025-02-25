import pandas as pd
import time

def calculer_inconnu():
    notes = []
    coeffs = []
    labels = []
    note_inconnue_label = "Inconnue"
    note_inconnue = None
    coeff_inconnu = 0
    
    print("Entrez vos notes et coefficients. Laissez la note vide pour l'inconnue.")
    
    while True:
        label = input("Nom de la matière ou de l'évaluation : ")
        note = input("Entrez une note (ou appuyez sur Entrée si c'est l'inconnue) : ")
        coeff = input("Entrez le coefficient correspondant : ")
        
        if not coeff.isdigit():
            print("Le coefficient doit être un nombre entier.")
            continue
        
        coeff = int(coeff)
        
        if note == "":
            coeff_inconnu = coeff
            note_inconnue_label = label
        else:
            try:
                note = float(note)
                notes.append(note * coeff)
                coeffs.append(coeff)
                labels.append((label, note, coeff))
            except ValueError:
                print("Veuillez entrer un nombre valide pour la note.")
                continue
        
        continuer = input("Voulez-vous ajouter une autre note ? (oui/non) : ").strip().lower()
        if continuer != "oui":
            break
    
    moyenne_cible = float(input("Entrez la moyenne cible : "))
    
    somme_notes_connues = sum(notes)
    somme_coeffs = sum(coeffs) + coeff_inconnu
    
    if coeff_inconnu > 0:
        note_inconnue = ((moyenne_cible * somme_coeffs) - somme_notes_connues) / coeff_inconnu
        labels.append((note_inconnue_label, note_inconnue, coeff_inconnu))
    else:
        note_inconnue = None
    
    df = pd.DataFrame(labels, columns=["Matière", "Note", "Coefficient"])
    print("\nRécapitulatif des notes :")
    print(df.to_string(index=False))
    if note_inconnue is not None :
        print(f"\nPour obtenir une moyenne de \033[92m {moyenne_cible} \033[0m  , la note inconnue doit être : \033[92m{note_inconnue:.2f} \033[0m ")
    
    if note_inconnue is not None and note_inconnue < 10:
        print("\n \033[92m La note inconnue calculée est tranquille à avoir atteindre.\033[0m")
    elif note_inconnue is not None and note_inconnue >=10 and note_inconnue <14:
        print("\n \033[93m La note inconnue calculée est possible à atteindre.\033[0m")
    elif note_inconnue is not None and note_inconnue >=14 and note_inconnue <20:
        print("\n \033[93m La note inconnue calculée est très chaud à atteindre. \033[0m")
    elif note_inconnue is not None and note_inconnue > 20:
        print("\n \033[91m La note inconnue calculée est impossible à atteindre tes mort bouffon. Ta raté ton année \033[0m")
    
    print("\nPropositions pour ajuster les autres notes afin de rendre la note inconnue plus raisonnable ou pour cibler les matières au rattrapage :")
    suggestions = []
    
    def generer_suggestions(labels, notes, coeffs, moyenne_cible, somme_notes_connues, somme_coeffs, coeff_inconnu, note_inconnue):
        increment = 0.01
        suggestions = []

        # Simple adjustments
        for i in range(len(notes)):
            note_orig = notes[i]
            while notes[i] <= 20:
                nouvelle_moyenne = (somme_notes_connues + (notes[i] - note_orig) * coeffs[i]) / somme_coeffs
                if note_inconnue is not None:
                    note_inconnue = ((moyenne_cible * somme_coeffs) - somme_notes_connues - (note_orig * coeffs[i]) + (notes[i] * coeffs[i])) / coeff_inconnu
                if nouvelle_moyenne >= moyenne_cible:
                    suggestions.append((labels[i], notes[i], nouvelle_moyenne))
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
                    suggestions.append((f"{labels[i]} et {labels[j]}", notes[i], notes[j], nouvelle_moyenne))
                    break
                notes[i] += increment
                notes[j] += increment
            notes[i] = note_orig_i  # Reset note to original value for next iteration
            notes[j] = note_orig_j  # Reset note to original value for next iteration
        
        return suggestions
    
    while True:
        start_time = time.time()
        if note_inconnue is None:
            suggestions = generer_suggestions(
                [label[0] for label in labels], [label[1] for label in labels], [label[2] for label in labels], moyenne_cible, somme_notes_connues, somme_coeffs, coeff_inconnu, note_inconnue
            )
        
            end_time = time.time()
            execution_time = end_time - start_time
            
            for idx, suggestion in enumerate(suggestions):
                if len(suggestion) == 3:
                    matiere, nouvelle_note, nouvelle_moyenne = suggestion
                    print(f"Suggestion \033[92m {idx+1} \033[0m  : Augmenter \033[92m {matiere}\033[0m à \033[92m{nouvelle_note:.2f}\033[0m pour atteindre une nouvelle moyenne de \033[92m{nouvelle_moyenne:.2f}\033[0m")
                elif len(suggestion) == 4:
                    matieres, nouvelle_note1, nouvelle_note2, nouvelle_moyenne = suggestion
                    print(f"Suggestion \033[92m {idx+1} \033[0m : Augmenter \033[92m {matieres} à \033[92m{nouvelle_note1:.2f}\033[0m et \033[92m{nouvelle_note2:.2f}\033[0m pour atteindre une nouvelle moyenne de \033[92m{nouvelle_moyenne:.2f}\033[0m")
            
            print(f"Temps d'exécution des suggestions : {execution_time:.2f} secondes")
            
            choix = input("Les suggestions vous conviennent-elles ? (oui/non) : ").strip().lower()
            if choix == "oui":
                break
            else:
                print("Génération de nouvelles suggestions en modifiant plusieurs notes...")
        else:
            break

            

    
calculer_inconnu()
