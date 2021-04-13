import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';
import {get_transformed_coordinates} from '../../../support/utils'

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

    })

    context('It Correctly Draws and Edits all Instance Types', () => {
      it('Correctly creates a bounding box.', () => {
        cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.wait(3000)
        const min_x = 75;
        const min_y = 75;
        const max_x = 120;
        const max_y = 120;
        cy.mousedowncanvas(min_x, min_y);
        cy.wait(500)

        cy.mouseupcanvas();
        cy.wait(1000)

        cy.mousedowncanvas(max_x, max_y);
        cy.wait(500)
        cy.mouseupcanvas();

        cy.wait(2000)

        cy.document().then((doc) => {
          cy.window().then((window) => {
            const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
            const annCore = window.AnnotationCore;
            const min_clientX = min_x + canvas_client_box.x;
            const min_clientY = min_y + canvas_client_box.y;
            const box_point_min = get_transformed_coordinates({x: min_clientX, y: min_clientY},
              canvas_client_box,
              annCore.canvas_transform,
              annCore.canvas_translate)
            const max_clientX = 120 + canvas_client_box.x;
            const max_clientY = 120 + canvas_client_box.y;
            const box_point_max = get_transformed_coordinates({x: max_clientX, y: max_clientY},
              canvas_client_box,
              annCore.canvas_transform,
              annCore.canvas_translate);
            expect(annCore.instance_list[0]).to.exist;
            expect(annCore.instance_list[0].x_min).to.equal(box_point_min.x);
            expect(annCore.instance_list[0].x_max).to.equal(box_point_max.x);
            expect(annCore.instance_list[0].y_min).to.equal(box_point_min.y);
            expect(annCore.instance_list[0].y_max).to.equal(box_point_max.y);
          })

        })
      })

      it('Correctly creates a polygon.', () => {
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Polygon').click({force: true})
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.wait(1000);
        const points = [
          {x: 200, y: 25},
          {x: 200, y: 60},
          {x: 180, y: 40},
          {x: 160, y: 10},
          {x: 200, y: 25},
        ]


        cy.mousedowncanvas(points[0].x, points[0].y);
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


        cy.document().then((doc) => {
          cy.window().then((window) => {
            const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
            const annCore = window.AnnotationCore;
            expect(annCore.instance_list[1]).to.exist;

            // We want to skip the last point since that is the initial point. That's why its length - 1
            for(let i = 0; i < points.length - 1; i++){
              const point = points[i];
              const clientX = point.x + canvas_client_box.x;
              const clientY = point.y + canvas_client_box.y;
              const box_point = get_transformed_coordinates({x: clientX, y: clientY},
                canvas_client_box,
                annCore.canvas_transform,
                annCore.canvas_translate)

              expect(annCore.instance_list[1].points[i].x).to.equal(box_point.x);
              expect(annCore.instance_list[1].points[i].y).to.equal(box_point.y);
            }


          })

        })

      })

      it('Correctly creates a point.', () => {
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Point').click({force: true})
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.wait(1000)
        const point = {x: 25, y:25};
        cy.mousedowncanvas(point.x, point.y);
        cy.mouseupcanvas()
        cy.wait(1000);
        cy.document().then((doc) => {
          cy.window().then((window) => {
            const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
            const annCore = window.AnnotationCore;

            const clientX = point.x + canvas_client_box.x;
            const clientY = point.y + canvas_client_box.y;
            const box_point = get_transformed_coordinates({x: clientX, y: clientY},
              canvas_client_box,
              annCore.canvas_transform,
              annCore.canvas_translate)
            expect(annCore.instance_list[2]).to.exist;
            expect(annCore.instance_list[2].points[0].x).to.equal(box_point.x);
            expect(annCore.instance_list[2].points[0].y).to.equal(box_point.y);
          })
        })
      })

      it('Correctly creates a Line.', () => {
        const points = [
          {x: 145, y: 145},
          {x: 220, y: 90},
        ]


        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Line').click({force: true})
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.wait(1000)
        cy.mousedowncanvas(points[0].x,points[0].y);
        cy.mouseupcanvas()

        cy.mousedowncanvas(points[1].x, points[1].y);
        cy.mouseupcanvas()
        cy.wait(2000)

        cy.document().then((doc) => {
          cy.window().then((window) => {
            const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
            const annCore = window.AnnotationCore;
            expect(annCore.instance_list[1]).to.exist;

            // We want to skip the last point since that is the initial point. That's why its length - 1
            for(let i = 0; i < points.length - 1; i++){
              const point = points[i];
              const clientX = point.x + canvas_client_box.x;
              const clientY = point.y + canvas_client_box.y;
              const box_point = get_transformed_coordinates({x: clientX, y: clientY},
                canvas_client_box,
                annCore.canvas_transform,
                annCore.canvas_translate)

              expect(annCore.instance_list[3].points[i].x).to.equal(box_point.x);
              expect(annCore.instance_list[3].points[i].y).to.equal(box_point.y);
            }


          })

        })


      })

      it('Correctly creates a Cuboid.', () => {
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Cuboid').click({force: true})
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.wait(3000)
        const rear_top_left = {x: 160, y: 160};
        const rear_bot_right = {x: 195, y: 180};
        const front_bot_right = {x: 215, y: 230};
        cy.mousedowncanvas(rear_top_left.x, rear_top_left.y);
        cy.mouseupcanvas()
        cy.mousedowncanvas(rear_bot_right.x, rear_bot_right.y);
        cy.mouseupcanvas()
        cy.mousedowncanvas(front_bot_right.x, front_bot_right.y);
        cy.mouseupcanvas()
        cy.document().then((doc) => {
          cy.window().then((window) => {
            const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
            const annCore = window.AnnotationCore;
            expect(annCore.instance_list[4]).to.exist;


            let clientX = rear_top_left.x + canvas_client_box.x;
            let clientY = rear_top_left.y + canvas_client_box.y;
            let box_point = get_transformed_coordinates({x: clientX, y: clientY},
              canvas_client_box,
              annCore.canvas_transform,
              annCore.canvas_translate)

            expect(annCore.instance_list[4].rear_face.top_left.x).to.equal(box_point.x);
            expect(annCore.instance_list[4].rear_face.top_left.y).to.equal(box_point.y);

            clientX = rear_bot_right.x + canvas_client_box.x;
            clientY = rear_bot_right.y + canvas_client_box.y;
            box_point = get_transformed_coordinates({x: clientX, y: clientY},
              canvas_client_box,
              annCore.canvas_transform,
              annCore.canvas_translate)

            expect(annCore.instance_list[4].rear_face.bot_right.x).to.equal(box_point.x);
            expect(annCore.instance_list[4].rear_face.bot_right.y).to.equal(box_point.y);

            clientX = front_bot_right.x + canvas_client_box.x;
            clientY = front_bot_right.y + canvas_client_box.y;
            box_point = get_transformed_coordinates({x: clientX, y: clientY},
              canvas_client_box,
              annCore.canvas_transform,
              annCore.canvas_translate)

            expect(annCore.instance_list[4].front_face.bot_right.x).to.equal(box_point.x);
            expect(annCore.instance_list[4].front_face.bot_right.y).to.equal(box_point.y);

          })

        })
      })

      it('Correctly creates an Ellipse.', () => {
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.get('.v-list.v-select-list div').contains('Ellipse').click({force: true})
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.wait(3000)
        const start = {x: 80, y: 175};
        const borders = {x: 135, y: 160};
        const center_x = Math.min(start.x, borders.x)
        const center_y = Math.min(start.y, borders.y)
        cy.mousedowncanvas(start.x, start.y);
        cy.mouseupcanvas()
        cy.wait(500)
        cy.mousedowncanvas(borders.x, borders.y);
        cy.mouseupcanvas()
        cy.wait(2000)

        cy.document().then((doc) => {
          cy.window().then((window) => {
            const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
            const annCore = window.AnnotationCore;
            expect(annCore.instance_list[5]).to.exist;


            let clientX = center_x + canvas_client_box.x;
            let clientY = center_y + canvas_client_box.y;
            let box_point = get_transformed_coordinates({x: clientX, y: clientY},
              canvas_client_box,
              annCore.canvas_transform,
              annCore.canvas_translate)

            expect(annCore.instance_list[5].center_x).to.equal(box_point.x);
            expect(annCore.instance_list[5].center_y).to.equal(box_point.y);

          })

        })
      })

      it('Correctly Saves The created instances', () => {
        cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
        cy.get('[data-cy="save_button"]').click({force: true})
        cy.wait('@annotation_update')
          .should(({request, response}) => {
            expect(request.method).to.equal('POST')
            // it is a good practice to add assertion messages
            // as the 2nd argument to expect()
            expect(response.statusCode, 'response status').to.eq(200)
          })
      })

      it('Correctly Switches to Edit Mode', () => {
        cy.get('[data-cy="edit_toggle"]').click({force: true})
        cy.get('[data-cy="edit_toggle"]').parent().parent().find('label').should('have.text', 'Editing')
        cy.wait(2000)
      })

      it('Should select and resize a box', () => {
        // Select Element
        cy.mousedowncanvas(80, 80);
        cy.mouseupcanvas()
        cy.wait(2000)
        cy.dragcanvas(75, 75, 50, 50);
        cy.wait(2000)
        cy.dragcanvas(120, 120, 95, 95);
        cy.wait(1000)

      })

      it('Should select and move a box', () => {
        // Select Element
        cy.mousedowncanvas(85, 50);
        cy.mouseupcanvas()
        cy.wait(2000)
        cy.dragcanvas(85, 85, 140, 140);
        cy.wait(1000)

      })

      it('Correcly Resizes a polygon', () => {
        cy.mousedowncanvas(190, 50);
        cy.mouseupcanvas()
        cy.wait(2000)
        cy.dragcanvas(180, 40, 100, 80);
        cy.wait(1000)

      })

      it('Correcly Moves a polygon', () => {
        cy.mousedowncanvas(170, 50);
        cy.mouseupcanvas()
        cy.wait(2000)
        cy.dragcanvas(170, 50, 150, 150);
        cy.wait(1000)

      })

      it('Correcly Moves a line', () => {
        cy.mousedowncanvas(145, 145);
        cy.mouseupcanvas()
        cy.wait(2000)
        cy.dragcanvas(145, 145, 180, 180);
        cy.wait(1000)

      })

      it('Correcly Moves a Cuboid', () => {
        // TODO: FOR SOME REASON THIS TEST IS NOT WORKING WHEN RUNNING CYPRESS HEADLESS. CHECK LATER
        cy.dragcanvas(160, 160, 135, 135);
        cy.wait(1000)

      })

      it('Correctly Saves The edited instances', () => {
        cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
        cy.get('[data-cy="save_button"]').click({force: true})
        cy.wait('@annotation_update')
          .should(({request, response}) => {
            expect(request.method).to.equal('POST')
            // it is a good practice to add assertion messages
            // as the 2nd argument to expect()
            expect(response.statusCode, 'response status').to.eq(200)
          })
      })
    })

  })

})
