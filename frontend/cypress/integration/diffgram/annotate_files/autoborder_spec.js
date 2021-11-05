import testUser from '../../../fixtures/users.json';

const points = [
  {x: 300, y: 25},
  {x: 400, y: 60},
  {x: 280, y: 40},
  {x: 260, y: 10},
  {x: 300, y: 25},
]

describe('Autoborder', () => {

  context('Autoborder', () => {

    before(function () {

      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // Straight to studio from login
      cy.loginByForm(testUser.email, testUser.password, "?redirect=%2Fstudio%2Fannotate%2Fdiffgram-testing-e2e");
      cy.wait(15000)
    })

    it('[Prep] Create a Polygon to Prepare', () => {
      cy.selectDrawValidatePolygon(points)
    })

    it('[UI] Shows AutoBorder General Info Prompt', () => {
      cy.get('[data-cy="ok_autoborder"]').click({force: true})
    })

    it('[Canvas] Selects First Autoborder Point (New Polygon)', () => {
      cy.mousedowncanvas(points[0].x, points[0].y);
      cy.mouseupcanvas()
    })

    it('[UI] Shows AutoBorder Point Selected Usage Prompt', () => {
      cy.get('[data-cy="auto_border_first_point_selected_usage_prompt"]').should('be.visible')
    })
   
    it('[Canvas] Selects Second Autoborder Point', () => {
      cy.mousedowncanvas(points[2].x, points[2].y);
      cy.mouseupcanvas()
    })

    it('[UI] Shows Second AutoBorder Prompt', () => {
      cy.get('[data-cy="auto_border_path_prompt"]').should('be.visible')
    })

    it('[UI] Selects Short Path', () => {
      cy.get('[data-cy="auto_border_path_prompt_short"]').should('be.visible')
      cy.get('[data-cy="auto_border_path_prompt_short"]').click()
    })

  })
})
