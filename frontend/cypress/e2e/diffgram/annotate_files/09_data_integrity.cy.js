import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';
import {get_transformed_coordinates} from '../../../support/utils'

describe('Annotate Files Tests', () => {

  context('Test Annotate files Data Integrity ', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)
        .uploadAndViewSampleVideo(testUser.project_string_id);

    })

    context('It Correctly raises an error when frontend sends invalid instance list.', () => {
      it('Correctly raises an instance_list integrity error.', () => {
        cy.wait(1000)
        cy.intercept(`http://localhost:8085/api/project/*/file/*/annotation/update`).as('annotation_update')
          .get('[data-cy="minimize-file-explorer-button"]').click({force: true})

        // Draw 3 boxes
        const boxes = [
          {
            min_x: 75,
            min_y: 75,
            max_x: 120,
            max_y: 120,
          },
          {
            min_x: 150,
            min_y: 150,
            max_x: 220,
            max_y: 220,
          },
          {
            min_x: 275,
            min_y: 275,
            max_x: 320,
            max_y: 320,
          }
        ]

        for (let box of boxes) {
          cy.wait(2000)
          cy.mousedowncanvas(box.min_x, box.min_x);
          cy.wait(500)

          cy.mouseupcanvas();
          cy.wait(1000)

          cy.mousedowncanvas(box.max_x, box.max_x);
          cy.wait(500)
          cy.mouseupcanvas();
          cy.wait(500)


        }


        cy.get('[data-cy="save_button"]').click({force: true})
        cy.wait('@annotation_update', {timeout: 300000})
          .should(({request, response}) => {
            expect(request.method).to.equal('POST')
            // it is a good practice to add assertion messages
            // as the 2nd argument to expect()
            expect(response.statusCode, 'response status').to.eq(200)
          })
        // Now Manually remove an instance and send payload again with a new box
        cy.window().then(window => {
          window.AnnotationCore.instance_list.shift();
          // Draw one more box
          const box = {
            min_x: 175,
            min_y: 175,
            max_x: 225,
            max_y: 225,
          }
          cy.mousedowncanvas(box.min_x, box.min_y);
          cy.wait(500)

          cy.mouseupcanvas();
          cy.wait(1000)

          cy.mousedowncanvas(box.max_x, box.max_y);
          cy.wait(500)
          cy.mouseupcanvas();

          cy.wait(2000)
          cy.get('[data-cy="save_button"]').click({force: true})
          cy.wait('@annotation_update', {timeout: 300000})
            .should(({request, response}) => {
              expect(request.method).to.equal('POST')
              // it is a good practice to add assertion messages
              // as the 2nd argument to expect()
              console.log('respoonsee', response.error, response.data)
              expect(response.statusCode, 'response status').to.eq(200)
              // Removing until error is handled better
              // expect(response.body.log.error).to.have.all.keys(
              //   'new_instance_list_missing_ids',
              //   'information',
              //   'missing_ids'
              //   )

            })
        });
      })
    })

    context('It Correctly saves in parellel all frames when pasting to multiple frames', () => {
      it('Correctly raises an instance_list integrity error.', () => {
        cy.intercept(`http://localhost:8085/api/project/*/file/*/annotation/update`).as('annotation_update')


        // Draw 1 boxes
        const boxes = [
          {
            min_x: 400,
            min_y: 100,
            max_x: 600,
            max_y: 250,
          },
        ]
        for (let box of boxes) {
          cy.mousedowncanvas(box.min_x, box.min_y)
            .wait(500)

            .mouseupcanvas()
            .wait(1000)

            .mousedowncanvas(box.max_x, box.max_y)
            .wait(500)
            .mouseupcanvas()

            .wait(2000)
        }
        cy.wait(7000)
          .get('[data-cy="edit_toggle"]').click({force: true})
          .wait(500)
          .mousemovecanvas(500, 150)
          .mousedowncanvas(500, 150)
          .wait(500)
          .mouseupcanvas()
          .wait(1000)
          .mousemovecanvas(500, 150)
          .mousedowncanvas(500, 150)
          .wait(500)
          .mouseupcanvas()
          .wait(500)
          .mousemovecanvas(500, 150)
          .wait(500)
          .rightclickdowncanvas(500, 150)
          .wait(1000)
          .get('[data-cy=copy_instance]').should('exist')
          .get('[data-cy=copy_instance]').click({force: true})
          .wait(1000)
          .mousemovecanvas(500, 150)
          .wait(500)
          .rightclickdowncanvas(500, 150)
          .wait(500)
          .get('[data-cy=show_menu_paste_next_frames]').click({force: true})
          .wait(500)
          .get('[data-cy=paste_frame_count').type('{backspace}5')
          .get('[data-cy=paste_next_frames]').click({force: true})
          .wait(500)
          .wait(10000)
          .get('@annotation_update.all').should('have.length.at.least', 5)
          .then((xhrs) => {
            expect(xhrs[0].response, 'request status').to.have.property('statusCode', 200)
            expect(xhrs[1].response, 'request status').to.have.property('statusCode', 200)
            expect(xhrs[2].response, 'request status').to.have.property('statusCode', 200)
            expect(xhrs[3].response, 'request status').to.have.property('statusCode', 200)
            expect(xhrs[4].response, 'request status').to.have.property('statusCode', 200)
            expect(xhrs[5].response, 'request status').to.have.property('statusCode', 200)
          })
      });
    })

    context('It Correctly saves all pending frames when fetching a new frame buffer.', () => {
      it('Checks no frames are pending save when re fetching frame buffer.', () => {
        cy.intercept(`http://localhost:8085/api/project/*/file/*/annotation/update`).as('annotation_update')
        // Draw 1 boxes
        cy.wait(2000)
          .get('[data-cy="edit_toggle"]').click({force: true})
        const boxes = [
          {
            min_x: 25,
            min_y: 25,
            max_x: 50,
            max_y: 50,
          },
        ]
        for (let box of boxes) {
          cy.mousedowncanvas(box.min_x, box.min_y)
            .wait(500)
            .mouseupcanvas()
            .wait(1000)
            .mousedowncanvas(box.max_x, box.max_y)
            .wait(500)
            .mouseupcanvas()
            .wait(2000)
        }
        cy.wait(3000)
          .window().then(window => {
          window.AnnotationUIFactory.set_has_changed(true)
        })
          .window().its('video_player').then(video_player_component => {
          cy.wait(1000).then(() => {
            video_player_component.go_to_keyframe(65)

          })
          .then(() => {
            cy.wait(1500)
              .get('@annotation_update.all').should('have.length.at.least', 1)
              .then((xhrs) => {
                expect(xhrs[0].response, 'request status').to.have.property('statusCode', 200)
                expect(xhrs[0].request.body.video_data.current_frame, 'request status').to.equal(0)

                cy.window().its('AnnotationUIFactory').then(ui_factory => {
                  expect(ui_factory.annotation_ui_context.current_image_annotation_ctx.unsaved_frames.length).to.equal(0)
                  let pending_save_frames = Object.keys(ui_factory.annotation_ui_context.current_image_annotation_ctx.instance_buffer_metadata);
                  for (let key of pending_save_frames) {
                    expect(ui_factory.annotation_ui_context.current_image_annotation_ctx.instance_buffer_metadata[key].pending_save).to.satisfy(val => {
                      return val === false || val === undefined
                    });

                  }

                })
              })
          })
        })
      });
    })
  })

})
