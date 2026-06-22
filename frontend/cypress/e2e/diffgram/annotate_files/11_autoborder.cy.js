// Import the test user data from the fixture file
import testUser from '../../../fixtures/users.json';

// Import the labels for attributes from the fixture file
import labelsForAttributes from "../../../fixtures/labelsForAttributes.json";

// Define the points for a polygon
const points = [
    {x: 200, y: 25},
    {x: 200, y: 60},
    {x: 180, y: 40},
    {x: 160, y: 10},
    {x: 200, y: 25},
];

// Describe the 'Autoborder' context
describe('Autoborder', () => {
  context('Autoborder', () => {

    // Set up the test environment before each test
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // Log in the test user and navigate to the studio
      cy.loginByForm(testUser.email, testUser.password, "?redirect=%2Fstudio%2Fannotate%2Fdiffgram-testing-e2e")
        // Create labels for attributes
        .createLabels(labelsForAttributes)
        // Upload and view the sample image twice
        .uploadAndViewSampleImage(testUser.project_string_id)
        .uploadAndViewSampleImage(testUser.project_string_id)
        // Wait for 15 seconds
        .wait(15000)
    })

    // Create a polygon to prepare
    it('[Prep] Create a Polygon to Prepare', () => {
      cy.selectDrawValidatePolygon(points)
    })

    // Verify that the general info prompt is shown
    it('[UI] Shows General Info Prompt', () => {
      cy.get('[data-cy="ok_autoborder"]').click({force: true})
    })

    // Select the first point of the polygon and verify that the point selected usage prompt is shown
    it('[Canvas] New Polygon & Selects First Autoborder Point', () => {
      cy.mousedowncanvas(points[0].x + 5, points[0].y + 5);
      cy.mouseupcanvas()

      cy.mousedowncanvas(points[0].x, points[0].y);
      cy.mouseupcanvas()
    })

    /*
    // Verify that the point selected usage prompt is shown
    it('[UI] Shows Point Selected Usage Prompt', () => {
      cy.get('[data-cy="minimize-file-explorer-button"]')
        .then($button => {
          console.log($button)
          if ($button.is(':visible')) {
              $button.click()
            }
          })
      cy.get('[data-cy="auto_border_first_point_selected_usage_prompt"]').should('be.visible')
    })
    */

    // Select the second point of the polygon
    it('[Canvas] Selects Second Autoborder Point', () => {
      cy.mousedowncanvas(points[2].x, points[2].y);
      cy.mouseupcanvas()
    })

    // Verify that the second prompt is shown
    it('[UI] Shows Second Prompt', () => {
      cy.get('[data-cy="auto_border_path_prompt"]').should('be.visible')
    })

    // Select the short path
    it('[UI] Selects Short Path', () => {
      cy.get('[data-cy="auto_border_path_prompt_short"]').should('be.visible')
      cy.get('[data-cy="auto_border_path_prompt_short"]').click()
    })

  })
})

