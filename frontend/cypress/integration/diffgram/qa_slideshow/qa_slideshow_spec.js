import testUser from "../../../fixtures/users.json";
import testLabels from "../../../fixtures/labels.json";

describe("Test set for QA slideshow", () => {
  before(function() {
    Cypress.Cookies.debug(true, { verbose: true });
    Cypress.Cookies.defaults({
      preserve: ["session"]
    });
    // login before all tests
    cy.loginByForm(testUser.email, testUser.password);
    cy.gotToProject(testUser.project_string_id);
    cy.createLabels(testLabels);
    cy.uploadAndViewSampleImage(testUser.project_string_id);
    cy.wait(3000);
    for (let i = 0; i < 3; i++) {
      cy.select_label("car");
      cy.mousedowncanvas(75, 75);
      cy.mouseupcanvas();
      cy.mousedowncanvas(120, 120);
      cy.mouseupcanvas();
      cy.wait(3000);
      cy.mousedowncanvas(90, 90);
      cy.mouseupcanvas();
    }
    cy.wait(3000);
  });

  it('[In Studio] Hides ghost instance info box to ensure out of way for instance templates', () => {
      cy.get('[data-cy=more_button]').click({force: true});
      cy.wait(100)
      cy.get('[data-cy=advanced_setting]').click({force: true})
      cy.wait(100)
      cy.get('[data-cy=show_ghost_instances]').click({force: true})
  })

  it("Tests if slideshow focuses on annotations correctly", () => {
    cy.get('[data-cy=more_button]').click({force: true});
    cy.wait(100)
    cy.get('[data-cy="open-annotation-show-menu"]').click();
    cy.wait(100);
    cy.get('[data-cy="start-annotation-show"]').click();
    cy.wait(3000);
    cy.get('[data-cy="show-progress-bar"]')
      .invoke("text")
      .then(initial_state => {
        cy.wait(1000);
        cy.get('[data-cy="show-progress-bar"]')
          .invoke("text")
          .then(finalS_state => {
            expect(initial_state).to.not.equal(finalS_state);
            cy.get('[data-cy=more_button]').click({force: true});
            cy.wait(100)
            cy.get('[data-cy="pause-annotation-show"]').click();
          });
      });
  });

  // Hide until call stacck exceeded fixed https://github.com/diffgram/diffgram/issues/410
  /*
  it("Tests if qa slideshow changes files correctly", () => {
    cy.location("search").then(loc => {
      cy.get('[data-cy="open-annotation-show-menu"]').click();
      cy.wait(100);
      cy.get('[data-cy="start-annotation-show"]').click();
      cy.wait(10000);
      cy.get('[data-cy="pause-annotation-show"]').click();
      cy.location("search").then(final => {
        expect(loc).to.not.equal(final);
      });
    });
  });
  */
});
