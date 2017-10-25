Feature: My OSIS
  Scenario:
    Given User "admin"/"admin" créé
    Given Je me connecte avec "admin"/"admin"
    And Je vais dans "My OSIS"
    Then Il y a "Profile"
    And Il y a "Messages"

  Scenario:
    Given User "admin"/"admin" créé
    Given Je me connecte avec "admin"/"admin"
    And Je vais dans "My OSIS"
#    Given Je suis sur la page "My OSIS"
    And Je click sur la page "Profile"
    Then Je vois 2 onglets
    Then Onglet 1 avec "Identification"
    Then Onglet 2 avec "Preferences"

  Scenario:
#    Given Je vais dans la page d'administration "/admin/base/person/add"
    Given J'ajoute une personne
    Then Je vais sur la page "Profile"
    And Je vois "WIRTEL, Stephane" comme titre
#
#  Scenario:
#    Given Je vais sur la page "Profile"
#    And Je selectionne l'onglet "Identification"
#    Then Je vois les champs suivants avec leur valeur
#      | field_name   | value    |
#      | fgs          | None     |
#      | first_name   | Stephane |
#      | last_name    | Wirtel   |
#      | gender       | U        |
#      | email        | -        |
#      | phone        | -        |
#      | mobile_phone | -        |
#      | language     | en       |
#
#  Scenario:
#    Given Je vais sur la page "Profile"
#    And Je selectionne l'onglet "Preferences"
#    Then La langue est "English"
