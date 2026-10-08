Feature: Weekly bills

  @REQ-weekly-bills-001
  Scenario: See the bills due in the next 7 days
    Given I have a bill due in 3 days
    And I have a bill due in 10 days
    When I open the home screen
    Then I see the bill due in 3 days
    And I do not see the bill due in 10 days

  @REQ-weekly-bills-003
  Scenario Outline: The list opens soon with many bills
    Given I have <amount> bills saved
    When I open the home screen
    Then I see the list within <seconds> seconds

    Examples:
      | amount | seconds |
      | 100    | 2       |
      | 500    | 2       |

  @REQ-weekly-bills-002
  Scenario: Undo a bill marked as paid by mistake
    Given I marked a bill as paid
    When I choose undo
    Then the bill goes back to the weekly list
