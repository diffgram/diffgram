import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";


describe('Annotate Files Tests', () => {

  context('Test Video Annotation', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.uploadAndViewSampleVideo(testUser.project_string_id);
      cy.wait(3500);

    })

    context('It Can Draw Boxes And Keep buffer dict references', () => {
      it('Draws a box on Video', () => {

        cy.window().then(window => {
          cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
          cy.select_label()
          cy.wait(3000)
          cy.mousedowncanvas(75, 75);
          cy.wait(500)

          cy.mouseupcanvas();
          cy.wait(1000)

          cy.mousedowncanvas(120, 120);
          cy.wait(500)
          cy.mouseupcanvas();

          cy.wait(2000)
          cy.log(window.AnnotationCore)
          expect(window.AnnotationCore.test_instance_list_and_list_in_buffer_by_ref()).to.equal(true);
        });

      })
      it('Moves 1 frame forward and backward keeping instance references', () => {

        cy.window().then(window => {

          cy.get('[data-cy="forward_1_frame"]').click({force: true})
          cy.wait(700)


          cy.wait(2000)

          cy.get('[data-cy="back_1_frame"]').click({force: true})
          cy.wait(2000)


          expect(window.AnnotationCore.test_instance_list_and_list_in_buffer_by_ref()).to.equal(true);
          // expect(window.AnnotationCore.instance_list[0].x_min).to.equal(true);
        });

      })

      it('Moves Box and change frames', () => {

        cy.window().then(window => {
          // Select Element

          cy.get('[data-cy="edit_toggle"]').click({force: true})
          cy.get('[data-cy="edit_toggle"]').parent().parent().find('label').should('have.text', 'Editing')
          cy.wait(2000)
          cy.mousedowncanvas(85, 50);
          cy.mouseupcanvas()
          cy.wait(2000)
          cy.dragcanvas(85, 85, 140, 140);
          cy.wait(3000)

          cy.get('[data-cy="forward_1_frame"]').click({force: true})
          cy.wait(2000)

          cy.get('[data-cy="back_1_frame"]').click({force: true})
          cy.wait(2000)

          expect(window.AnnotationCore.test_instance_list_and_list_in_buffer_by_ref()).to.equal(true);

        });

      })

      it('Shows Ghost Instances', () => {
        cy.get('[data-cy="edit_toggle"]').click({force: true})
          .wait(1000)
          .get('[data-cy="edit_toggle"]').parent().parent().find('label').should('have.text', 'Drawing')
          .wait(1000)
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .wait(2000)
          .window().then(window => {
          cy.wait(2000)
          expect(window.AnnotationCore.ghost_instance_list.length).to.be.at.least(1);

        });

      })


    })
  })

})
