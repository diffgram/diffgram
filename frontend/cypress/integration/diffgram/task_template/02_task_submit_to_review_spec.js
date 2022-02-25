import testUser from "../../../fixtures/users.json";
import testLabels from "../../../fixtures/labels.json";

describe("Correctly Submits Task to Review", () => {
  context("task review context", () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({preserve: ["session"]})

      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)
        .createSampleTasksUsingBackend(10)
    });

    it("Submits a task to review", () => {
      const url = "/api/v1/task/*/complete";

        cy.visit(`http://localhost:8085/job/list`)
        .wait(2000)
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
        .wait(6000)
        .intercept(url).as("submit_to_review")
        .get('[data-cy="submit-to-review"]').click({force: true})
        .wait("@submit_to_review")
        .its("response")
        .should("have.property", "statusCode", 200)
        .wait(6000)
        .get('[data-cy="go-to-task-list"]').click({force: true});
    });

    it("Reviews a task", () => {
      const url = "/api/v1/task/*/review";
      cy.visit(`http://localhost:8085/job/list`)
        .wait(2000)
        .get(`.job-card`)
        .first()
        .find('.job-title')
        .parent()
        .click({force: true})
        .wait(6000)
        .get("tbody > tr")
        .first()
        .click({force: true})
        .wait(6000)
        .intercept(url).as("review_task")
        .wait(2000)
        .get('[data-cy="submit-to-review"]').click({force: true})
        .wait(2000)
        .get('[data-cy="review-the-task"]').click({force: true})
        .wait("@review_task")
        .its("response")
        .should("have.property", "statusCode", 200);
    });
  });
})
;
