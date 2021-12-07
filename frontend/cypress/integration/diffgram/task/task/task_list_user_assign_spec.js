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

    it("Assign user to multiple tasks", () => {
      const url = "/api/v1/project/*/task/*/user/add";
      cy.get('[data-cy="show-hide-columns"]').click({ force: true });
      cy.get('[data-cy="select-column"]').click({ force: true });
      cy.get('[class="v-list-item__title"]')
        .first()
        .click({ force: true });
      cy.get("body").type("{esc}");
      cy.get("body").type("{esc}");
      cy.get('[data-cy="select-task-list-item"]')
        .eq(0)
        .click({ force: true });
      cy.get('[data-cy="select-task-list-item"]')
        .eq(1)
        .click({ force: true });
      cy.get('[data-cy="select-task-list-item"]')
        .eq(2)
        .click({ force: true });
      cy.get('[data-cy="select-task-list-action"]').click({ force: true });
      cy.get("div")
        .contains("Assign annotators")
        .click({ force: true });
      cy.wait(500);
      cy.get('[data-cy="add-batch-annotators-open"]').click({ force: true });
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
