 import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';
import {get_transformed_coordinates} from '../../../support/utils'

describe('Annotate Files Tests', () => {

  context('It Correctly Draws and Edits all Instance Types', () => {

    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all test
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)
        .uploadAndViewSampleImage(testUser.project_string_id);
    })

    it('Correctly creates a bounding box.', () => {
      const min_x = 75;
      const min_y = 75;
      const max_x = 120;
      const max_y = 120;
      cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
      .wait(3000)
      .select_label()

      .mousemovecanvas(min_x, min_y)
      .mousedowncanvas(min_x, min_y)
      .wait(500)

      .mouseupcanvas()
      .wait(500)
      .mousemovecanvas(max_x, max_y)
      .wait(500)

      .mousedowncanvas(max_x, max_y)
      .wait(500)
      .mouseupcanvas()

      .wait(2000)

      .document().then((doc) => {
        cy.window().then((window) => {

          const annCore = window.AnnotationCore;
          let canvas_wrapper_id = `canvas_wrapper`
          if(annCore){
            canvas_wrapper_id = `canvas_wrapper_${annCore.working_file.id}`
          }

          const canvas_wrapper = doc.getElementById(canvas_wrapper_id);
          const canvas_client_box = doc.getElementById(canvas_wrapper_id).getBoundingClientRect();
          const min_clientX = min_x + canvas_client_box.x;
          const min_clientY = min_y + canvas_client_box.y;
          cy.log(`min client_x ${min_clientX} min client y ${min_clientY}`)
          cy.log(`canvas_client_box x ${canvas_client_box.x} canvas_client_box y ${canvas_client_box.y}`)
          const box_point_min = get_transformed_coordinates({
            x: min_clientX,
            y: min_clientY
          }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx)
          cy.log(`min box_point_min ${box_point_min}`)
          const max_clientX = max_x + canvas_client_box.x;
          const max_clientY = max_y + canvas_client_box.y;
          const box_point_max = get_transformed_coordinates({
            x: max_clientX,
            y: max_clientY
          }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx);
          expect(annCore.instance_list[0]).to.exist;
          expect(annCore.instance_list[0].x_min).to.approximately(box_point_min.x + 1, 5);
          expect(annCore.instance_list[0].x_max).to.approximately(box_point_max.x, 5);
          expect(annCore.instance_list[0].y_min).to.approximately(box_point_min.y + 1, 5);
          expect(annCore.instance_list[0].y_max).to.approximately(box_point_max.y + 1, 5);
        })

      })
    })

    it('Correctly creates a polygon.', () => {
      cy.wait(3000)
      cy.mousemovecanvas(0,0)
      cy.selectDrawValidatePolygon()

    })

    it('Correctly creates a point.', () => {
      cy.get('[data-cy="instance-type-select"]').click({force: true})
      cy.get('.v-list.v-select-list div').contains('Point').click({force: true})
      cy.select_label()
      cy.wait(1000)
      const point = {x: 25, y: 25};
      cy.mousedowncanvas(point.x, point.y);
      cy.mouseupcanvas()
      cy.wait(1000);
      cy.document().then((doc) => {
        cy.window().then((window) => {
          const annCore = window.AnnotationCore;
          let canvas_wrapper_id = `canvas_wrapper`
          if(annCore){
            canvas_wrapper_id = `canvas_wrapper_${annCore.working_file.id}`
          }
          const canvas_wrapper = doc.getElementById(canvas_wrapper_id);
          const canvas_client_box = doc.getElementById(canvas_wrapper_id).getBoundingClientRect();


          const clientX = point.x + canvas_client_box.x;
          const clientY = point.y + canvas_client_box.y;
          const box_point = get_transformed_coordinates({
            x: clientX,
            y: clientY
          }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx)
          expect(annCore.instance_list[2]).to.exist;
          expect(annCore.instance_list[2].points[0].x).to.approximately(box_point.x, 2);
          expect(annCore.instance_list[2].points[0].y).to.approximately(box_point.y, 2);
        })
      })
    })

    it('Correctly creates a Line.', () => {
      const points = [{x: 145, y: 145}, {x: 220, y: 90},]


      cy.get('[data-cy="instance-type-select"]').click({force: true})
      cy.get('.v-list.v-select-list div').contains('Line').click({force: true})
      cy.select_label()
      cy.wait(1000)
      cy.mousedowncanvas(points[0].x, points[0].y);
      cy.mouseupcanvas()

      cy.mousedowncanvas(points[1].x, points[1].y);
      cy.mouseupcanvas()
      cy.wait(2000)

      cy.document().then((doc) => {
        cy.window().then((window) => {
          const annCore = window.AnnotationCore;
          let canvas_wrapper_id = `canvas_wrapper`
          if(annCore){
            canvas_wrapper_id = `canvas_wrapper_${annCore.working_file.id}`
          }
          const canvas_wrapper = doc.getElementById(canvas_wrapper_id);
          const canvas_client_box = doc.getElementById(canvas_wrapper_id).getBoundingClientRect();

          expect(annCore.instance_list[1]).to.exist;

          // We want to skip the last point since that is the initial point. That's why its length - 1
          for (let i = 0; i < points.length - 1; i++) {
            const point = points[i];
            const clientX = point.x + canvas_client_box.x;
            const clientY = point.y + canvas_client_box.y;
            const box_point = get_transformed_coordinates({
              x: clientX,
              y: clientY
            }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx)

            expect(annCore.instance_list[3].points[i].x).to.approximately(box_point.x, 4);
            expect(annCore.instance_list[3].points[i].y).to.approximately(box_point.y, 4);
          }


        })

      })


    })

    it('Correctly creates a Cuboid.', () => {
      cy.get('[data-cy="instance-type-select"]').click({force: true})
      cy.get('.v-list.v-select-list div').contains('Cuboid').click({force: true})
      cy.select_label()
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
          const annCore = window.AnnotationCore;
          let canvas_wrapper_id = `canvas_wrapper`
          if(annCore){
            canvas_wrapper_id = `canvas_wrapper_${annCore.working_file.id}`
          }
          const canvas_client_box = doc.getElementById(canvas_wrapper_id).getBoundingClientRect();

          expect(annCore.instance_list[4]).to.exist;


          let clientX = rear_top_left.x + canvas_client_box.x;
          let clientY = rear_top_left.y + canvas_client_box.y;
          const canvas_wrapper = doc.getElementById(canvas_wrapper_id);
          let box_point = get_transformed_coordinates({
            x: clientX,
            y: clientY
          }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx)

          expect(annCore.instance_list[4].rear_face.top_left.x).to.approximately(box_point.x, 4);
          expect(annCore.instance_list[4].rear_face.top_left.y).to.approximately(box_point.y, 4);

          clientX = rear_bot_right.x + canvas_client_box.x;
          clientY = rear_bot_right.y + canvas_client_box.y;
          box_point = get_transformed_coordinates({
            x: clientX,
            y: clientY
          }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx)

          expect(annCore.instance_list[4].rear_face.bot_right.x).to.approximately(box_point.x, 4);
          expect(annCore.instance_list[4].rear_face.bot_right.y).to.approximately(box_point.y, 4);

          clientX = front_bot_right.x + canvas_client_box.x;
          clientY = front_bot_right.y + canvas_client_box.y;
          box_point = get_transformed_coordinates({
            x: clientX,
            y: clientY
          }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx)

          expect(annCore.instance_list[4].front_face.bot_right.x).to.approximately(box_point.x, 4);
          expect(annCore.instance_list[4].front_face.bot_right.y).to.approximately(box_point.y, 4);

        })

      })
    })

    it('Correctly creates an Ellipse.', () => {
      cy.get('[data-cy="instance-type-select"]').click({force: true})
      cy.get('.v-list.v-select-list div').contains('Ellipse').click({force: true})
      cy.select_label()
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
          const annCore = window.AnnotationCore;
          let canvas_wrapper_id = `canvas_wrapper`
          if(annCore){
            canvas_wrapper_id = `canvas_wrapper_${annCore.working_file.id}`
          }
          const canvas_client_box = doc.getElementById(canvas_wrapper_id).getBoundingClientRect();
          const canvas_wrapper = doc.getElementById(canvas_wrapper_id);
          expect(annCore.instance_list[5]).to.exist;


          let clientX = center_x + canvas_client_box.x;
          let clientY = center_y + canvas_client_box.y;
          let box_point = get_transformed_coordinates({
            x: clientX,
            y: clientY
          }, canvas_client_box, annCore.canvas_element, canvas_wrapper, annCore.canvas_element_ctx)

          expect(annCore.instance_list[5].center_x).to.approximately(box_point.x, 4);
          expect(annCore.instance_list[5].center_y).to.approximately(box_point.y, 4);

        })

      })
    })

    it('Correctly Saves The created instances', () => {
      cy.wait(2000)
        .intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
        .window().then((window) => {
        window.AnnotationCore.has_changed = true;
      })
        .get('[data-cy="save_button"]').click({force: true})
        .wait('@annotation_update')
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
      cy.wait(500)
      cy.dragcanvas(145, 145, 350, 350);
      cy.wait(1000)

    })

    it('Correcly Moves a Cuboid', () => {
      cy.get('[data-cy="ok_autoborder"]').click({force: true})
        .mousedowncanvas(180, 180)
        .mouseupcanvas()
        .dragcanvas(180, 180, 225, 225)
        .wait(1000)

    })

    it('Correctly Saves The edited instances', () => {
      cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
      .wait(5000)
      .window().then((window) => {
        window.AnnotationCore.has_changed = true;
        window.AnnotationCoreToolbar.has_changed = true;
      })
      .then(() => {
        cy.get('[data-cy="save_button"]').click({force: true})
          .wait('@annotation_update', {timeout: 10000})
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
