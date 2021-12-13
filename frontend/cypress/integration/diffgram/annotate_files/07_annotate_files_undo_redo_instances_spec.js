import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('Annotate Files Tests', () => {

  context('Test Annotate files Main Features', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.uploadAndViewSampleImage(testUser.project_string_id);
      // Minimize file explorer
      cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
      // Select Label
      cy.select_label()
    })

    context('Undo/Redo All Instance Type Creations', () => {
      it('Correctly Undos a Bounding Box Creation', () => {
        // Draw box
        cy.wait(1000)
        cy.mousedowncanvas(75, 75);
        cy.wait(500)
        cy.mouseupcanvas();
        cy.wait(1000)
        cy.mousedowncanvas(120, 120);
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undo a Polygon Creation', () => {
        // Draw Polygon
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Polygon').click({force: true})
        cy.mousedowncanvas(200, 25);
        cy.mouseupcanvas()
        cy.mousedowncanvas(200, 60);
        cy.mouseupcanvas()
        cy.mousedowncanvas(180, 40);
        cy.mouseupcanvas()
        cy.mousedowncanvas(160, 10);
        cy.mouseupcanvas()
        cy.mousedowncanvas(200, 25);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');


      })

      it('Correctly Undo Line Creation', () => {
        // Draw Polygon
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Line').click({force: true})
        cy.mousedowncanvas(145, 145);
        cy.mouseupcanvas()
        cy.mousedowncanvas(220, 90);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undo Point Creation', () => {
        // Draw Point
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Point').click({force: true})
        cy.mousedowncanvas(25, 25);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undo Cuboid Creation', () => {
        // Draw Cuboid
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Cuboid').click({force: true})
        cy.mousedowncanvas(160, 160);
        cy.mouseupcanvas()
        cy.mousedowncanvas(195, 180);
        cy.mouseupcanvas()
        cy.mousedowncanvas(215, 230);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undo Ellipse Creation', () => {
        // Draw Ellipse
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Ellipse').click({force: true})
        cy.mousedowncanvas(80, 175);
        cy.mouseupcanvas()
        cy.wait(500)
        cy.mousedowncanvas(135, 160);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })



    })
    context('Undo all instance type editions', () =>{
      before(() =>{

      })

      it('Correctly Undos a Bounding Box Edition', () => {
        // Draw box
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Box').click({force: true})
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();
        cy.wait(1000)
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.wait(1000)
        cy.dragcanvas(75, 75, 50, 50);
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undos a Polygon Edition', () => {
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Polygon').click({force: true})
        cy.mousedowncanvas(200, 25);
        cy.mouseupcanvas()
        cy.mousedowncanvas(200, 60);
        cy.mouseupcanvas()
        cy.mousedowncanvas(180, 40);
        cy.mouseupcanvas()
        cy.mousedowncanvas(160, 10);
        cy.mouseupcanvas()
        cy.mousedowncanvas(200, 25);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.wait(1000)
        cy.dragcanvas(180, 40, 100, 100);
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undos a Line Edition', () => {
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Line').click({force: true})
        cy.mousedowncanvas(145, 145);
        cy.mouseupcanvas()
        cy.mousedowncanvas(220, 90);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.wait(1000)
        cy.dragcanvas(145, 145, 90, 90);
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })


      it('Correctly Undos a Point Edition', () => {
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Point').click({force: true})
        cy.mousedowncanvas(25, 25);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.wait(1000)
        cy.dragcanvas(25, 25, 84, 84);
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undos a Cuboid Edition', () => {
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Cuboid').click({force: true})
        cy.mousedowncanvas(160, 160);
        cy.mouseupcanvas()
        cy.mousedowncanvas(195, 180);
        cy.mouseupcanvas()
        cy.mousedowncanvas(215, 230);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.wait(1000)
        cy.dragcanvas(160, 160, 130, 130);
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');

      })

      it('Correctly Undos an Ellipse Edition', () => {
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Ellipse').click({force: true})
        cy.mousedowncanvas(80, 175);
        cy.mouseupcanvas()
        cy.wait(500)
        cy.mousedowncanvas(135, 160);
        cy.mouseupcanvas()
        cy.wait(1000)
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.wait(1000)
        cy.dragcanvas(90, 150, 80, 200);
        cy.wait(1000)
        cy.get('body').type('{ctrl+z}');
      })


    })
  })

})
