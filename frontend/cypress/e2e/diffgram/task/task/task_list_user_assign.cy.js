import testUser from "../../../../fixtures/users.json";

describe("manual_user_assignment", () => {
  context("manual_user_assignment", () => {
    before(function() {


      Cypress.Cookies.debug(true, { verbose: true });

      cy.loginByForm(testUser.email, testUser.password)
      .gotToProject(testUser.project_string_id)
      .createSampleTasksUsingBackend(10)

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
      cy.get('[data-cy="member-select-assign-task"]').first().click({ force: true });
      cy.get('[data-cy="member-select-assign-task__select-user"]')
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
      cy.get('[data-cy="add-batch-annotators-open"]').first().click({ force: true });
      cy.get('[data-cy="member-select-assign-task"]').first().click({ force: true });
      cy.get('[data-cy="member-select-assign-task__select-user"]')
        .first()
        .click({ force: true });
      cy.intercept(url).as("assign_user");
      cy.get('[data-cy="finish-user-assignment"]').click({ force: true });
      cy.wait("@assign_user")
        .its("response")
        .should("have.property", "statusCode", 200);
    });

    it("Unassign users to multiple tasks", () => {
      const url = "/api/v1/project/*/task/*/user/remove";
      cy.get('[data-cy="select-task-list-item"]')
        .eq(0)
        .click({ force: true })
        .get('[data-cy="select-task-list-item"]')
        .eq(1)
        .click({ force: true })
        .get('[data-cy="select-task-list-item"]')
        .eq(2)
        .click({ force: true })
        .wait(1500)
        .get('[data-cy="select-task-list-action"]').click({ force: true })
        .get("div")
        .contains("Remove annotators")
        .click({ force: true })
        .wait(1500)
        .get('[data-cy="remove-batch-annotators-open"]').click({ force: true })
        .get('[data-cy="member-select-assign-task"]').first().click({ force: true })
        .get('[data-cy="member-select-assign-task__select-user"]')
        .first()
        .click({ force: true })
        .intercept(url).as("remove_user")
        .get('[data-cy="finish-user-assignment"]').click({ force: true })
        .wait("@remove_user")
        .its("response")
        .should("have.property", "statusCode", 200);
    });
  });
});
