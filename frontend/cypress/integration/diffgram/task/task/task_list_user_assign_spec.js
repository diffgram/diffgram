import testUser from "../../../../fixtures/users.json";

describe("manual_user_assignment", () => {
  context("manual_user_assignment", () => {
    before(function() {
      cy.createSampleTasksUsingBackend(10);

      Cypress.Cookies.debug(true, { verbose: true });
      Cypress.Cookies.defaults({
        preserve: ["session"]
      });
      cy.loginByForm(testUser.email, testUser.password);
    });

    it("Assign user to one task", () => {
      const url = "/api/v1/project/*/task/*/user/modify";
      cy.visit(`http://localhost:8085/job/list`);
      cy.get('[data-cy="view_button"]')
        .first()
        .click({ force: true });
      cy.get('[data-cy="open-add-assignee-dialog"]')
        .first()
        .click({ force: true });
      cy.get('[data-cy="member-select"]').click({ force: true });
      cy.get('[data-cy="member-select__select-user"]')
        .first()
        .click({ force: true });
      cy.intercept(url).as("assign_user");
      cy.get('[data-cy="finish-user-assignment"]').click({ force: true });
      cy.wait("@assign_user")
        .its("response")
        .should("have.property", "statusCode", 200);
    });
  });
});
