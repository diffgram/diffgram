import testUser from "../../../fixtures/users.json";

describe("tasks_detail_pagination", () => {
  context("tasks_detail_pagination", () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({preserve: ["session"]})
      cy.createSampleTasksUsingBackend(10)
        .loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .create_task_template()
    });

    it("Submit task to review", () => {
      const url = "/api/v1/task/*/complete";
      cy.visit(`http://localhost:8085/job/list`)
        .get('@task_template_name')
        .then(task_template_name => {
          cy.get(`.${task_template_name.replace(/\s+/g, '')}`)
            .first()
            .find('.job-title')
            .parent()
            .click({force: true})
        })
        .wait(2000)
        .get("tbody > tr")
        .first()
        .click({force: true})
        .wait(3000)
        .intercept(url).as("submit_to_review")
        .get('[data-cy="submit-to-review"]').click({force: true})
        .wait("@submit_to_review")
        .its("response")
        .should("have.property", "statusCode", 200)
        .wait(3000)
        .get('[data-cy="go-to-task-list"]').click({force: true});
    });

    it("Reviews task", () => {
      const url = "/api/v1/task/*/review";
      cy.wait(2000);
      cy.get(".image-preview")
        .first()
        .click({force: true});
      cy.wait(3000);
      cy.intercept(url).as("review_task");
      cy.get('[data-cy="submit-to-review"]').click({force: true});
      cy.wait(2000);
      cy.get('[data-cy="review-the-task"]').click({force: true});
      cy.wait("@review_task")
        .its("response")
        .should("have.property", "statusCode", 200);
    });
  });
});
