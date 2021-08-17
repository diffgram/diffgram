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
        let url = '/api/project/*/file/*/annotation/update'
        cy.intercept(url).as('save_instances')
        cy.window().then(window => {
          cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
          .select_label()
          .wait(3000)
          .mousedowncanvas(75, 75)
          .wait(500)

          .mouseupcanvas()
          .wait(1000)

          .mousedowncanvas(160, 160)
          .wait(500)
          .mouseupcanvas()
          .wait(1000)

          .wait(7000)
          .wait('@save_instances', {timeout: 60000}).should(({request, response}) => {
            expect(request.method).to.equal('POST')
            expect(response.statusCode, 'response status').to.eq(200)

          })
          .log(window.AnnotationCore)
          expect(window.AnnotationCore.test_instance_list_and_list_in_buffer_by_ref()).to.equal(true);
        });

      })
      it('Moves 1 frame forward and backward keeping instance references', () => {

        cy.window().then(window => {
          cy.wait(1000)
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .wait(7000)
          .get('[data-cy=ghost_instance_ok]').click({force: true})
          .wait(7000)
          .get('[data-cy="back_1_frame"]').click({force: true})
          .wait(8000)


          expect(window.AnnotationCore.test_instance_list_and_list_in_buffer_by_ref()).to.equal(true);
          // expect(window.AnnotationCore.instance_list[0].x_min).to.equal(true);
        });

      })

      it('Shows Ghost Instances', () => {
        cy.wait(2000)
          .get('[data-cy="edit_toggle"]').click({force: true})
          .wait(5000)
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .wait(7000)
          .get('[data-cy=ghost_instance_ok]').click({force: true})

          .window().then(window => {
            expect(window.AnnotationCore.ghost_instance_list.length).to.be.at.least(1);

          })
          .wait(7000)
          .get('[data-cy="back_1_frame"]').click({force: true})

      })

      it('Moves Box and change frames', () => {
        let url = '/api/project/*/file/*/annotation/update'
        cy.intercept(url).as('save_instances')
        // Select Element
          .get('[data-cy="edit_toggle"]').parent().parent().find('label').should('have.text', 'Editing')
          .wait(2000)
        cy.mousedowncanvas(100, 100)
        cy.mouseupcanvas()
        cy.wait(2000)
        cy.dragcanvas(100, 100, 200, 200)

        cy.wait(2500)
        cy.get('[data-cy=save_button]').click({force: true})
          .wait('@save_instances').should(({request, response}) => {
            expect(request.method).to.equal('POST')
            expect(response.statusCode, 'response status').to.eq(200)

          })
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .wait(7000)
          .get('[data-cy="back_1_frame"]').click({force: true})
          .wait(7000)
          .window().then(window => {

            expect(window.AnnotationCore.test_instance_list_and_list_in_buffer_by_ref()).to.equal(true);
          });

      })



    })

    context('It Disables Pasting Multiple Instances and triggering cache error', () => {
      it('Can Copy and paste instances cross frames without breaking cache', () => {

        cy.get('[data-cy="forward_1_frame"]').click({force: true})
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .get('[data-cy="forward_1_frame"]').click({force: true})
          .get('[data-cy="edit_toggle"]').click({force: true})
          .select_label()
          .wait(2000)
          // Draw a box
          .mousedowncanvas(75, 75)
          .wait(500)

          .mouseupcanvas()
          .wait(1000)

          .mousedowncanvas(160, 160)
          .wait(500)
          .mouseupcanvas()
          .wait(1000)

          .wait(7000)
          .get('[data-cy="edit_toggle"]').click({force: true})
          .wait(2000)
          // Select uppermost box
          .mousedowncanvas(90, 90)
          .wait(500)
          .mouseupcanvas()
          .wait(1000)
        cy.window().then(window => {
          cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
            // Move 5 frames

            // Copy and paste on next frame Paste
            .get(`#canvas_wrapper`).type('{ctrl} + c',{force: true})
            .wait(2000)
            .then(()=>{
              cy.get('[data-cy="forward_1_frame"]').click({force: true})
                .wait(2000).then(() =>{
                  let instance_dup = {...window.AnnotationCore.instance_buffer_dict[6][0]};
                  window.AnnotationCore.instance_list.push({...instance_dup, id: null});
                  window.AnnotationCore.instance_list.push({...instance_dup, id: null});
                  window.AnnotationCore.instance_list.push({...instance_dup, id: null});
                  window.AnnotationCore.instance_list.push({...instance_dup, id: null});
                  window.AnnotationCore.has_changed = true;
                  cy.get('[data-cy=save_button]').click({force: true})
                    .wait(2000)
                    .get('[data-cy=save_warning]').should('be.visible')

              })

          })



        });

      })


    })
  })

})
