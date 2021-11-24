import testUser from "../../../fixtures/users.json";

describe("tasks_detail_pagination", () => {
  context("tasks_detail_pagination", () => {
    before(function() {
      cy.createSampleTasksUsingBackend(10);

      Cypress.Cookies.debug(true, { verbose: true });
      Cypress.Cookies.defaults({
        preserve: ["session"]
      });
      cy.loginByForm(testUser.email, testUser.password);
    });

    it("Submit task to review", () => {
      const url = "/api/v1/task/*/complete";
      cy.visit(`http://localhost:8085/job/list`);
      cy.get('[data-cy="view_button"]')
        .first()
        .click({ force: true });
      cy.wait(2000);
      cy.get("tbody > tr")
        .first()
        .click({ force: true });
      cy.wait(3000);
      cy.intercept(url).as("submit_to_review");
      cy.get('[data-cy="submit-to-review"]').click({ force: true });
      cy.wait("@submit_to_review")
        .its("response")
        .should("have.property", "statusCode", 200);
      cy.wait(3000);
      cy.get('[data-cy="go-to-task-list"]').click({ force: true });
    });

    it("Reviews task", () => {
      const url = "/api/v1/task/*/review";
      cy.wait(2000);
      cy.get("tbody > tr")
        .first()
        .click({ force: true });
      cy.wait(3000);
      cy.intercept(url).as("review_task");
      cy.get('[data-cy="submit-to-review"]').click({ force: true });
      cy.wait(2000);
      cy.get('[data-cy="review-the-task"]').click({ force: true });
      cy.wait("@review_task")
        .its("response")
        .should("have.property", "statusCode", 200);
    });
  });
});
