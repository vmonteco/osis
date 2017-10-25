Feature: Je me connecte a OSIS

  Scenario: Je me connecte avec mon compte
    Given User "admin"/"admin" créé
    Then Je me connecte avec "admin"/"admin"
    Then Je vois l'option Logout
    And Je me deconnecte

  Scenario: Je me connecte avec un mauvais password
    Given User "admin"/"admin" créé
    Then Je me connecte avec "admin"/"demo"
    Then J'ai le message "Your username and password didn't match. Please try again."