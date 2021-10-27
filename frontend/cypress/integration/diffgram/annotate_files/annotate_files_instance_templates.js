import testUser from '../../../fixtures/users.json';
import labelsForAttributes from '../../../fixtures/labelsForAttributes.json';
import testLabels from "../../../fixtures/labels.json";


describe('Annotate Files Tests', () => {

  context('Test Instance Templates Feature', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);

    })

    context('Creates an Instance Template', () => {

      it('Creates Instance Template', () => {
        cy.createInstanceTemplate('instance template 1', {
          nodes: [{x: 100, y: 100}, {x: 300, y: 300}, {x: 400, y: 400}, {x: 75, y: 150}],
          edges: [[0, 1], [0, 2], [0, 3]],
        });
        cy.get('[data-cy=save_instance_template_button]').click({force: true});
        cy.wait(5000);
      })
    })

    context('It edits an instance template.', () => {
      const template_name = 'instance template for edit';
      const nodes = [{x: 100, y: 100}, {x: 300, y: 300}, {x: 400, y: 400}, {x: 75, y: 150}];
      before(function () {
        Cypress.Cookies.debug(true, {verbose: true})
        Cypress.Cookies.defaults({
          preserve: ['session']
        })
        // login before all tests
        cy.loginByForm(testUser.email, testUser.password);
        cy.gotToProject(testUser.project_string_id);

      })

      it('Edits Instance Template Name', () => {
        cy.createInstanceTemplate(template_name, {
          nodes: nodes,
          edges: [[0, 1], [0, 2], [0, 3]],
        });
        cy.wait(5000);
        cy.get('[data-cy=instance_template_name_text_field]').type('{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}');

      })
      it('Edits Instance Template Nodes', () => {
        cy.get('[data-cy=edit_toggle_instance_template_create]').click({force: true});
        cy.get('[data-cy=instance_template_name_text_field]').type('{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}');
        cy.mousemovecanvas(nodes[0].x, nodes[0].y);
        cy.dragcanvas(nodes[0].x, nodes[0].y, nodes[0].x + 85, nodes[0].y);

        cy.get('[data-cy=save_instance_template_button]').click({force: true});
      })
    })

    context('It Draws an instance template', () => {
      const nodes = [{x: 100, y: 100}, {x: 300, y: 300}, {x: 400, y: 400}, {x: 75, y: 150}];
      before(function () {
        Cypress.Cookies.debug(true, {verbose: true})
        Cypress.Cookies.defaults({
          preserve: ['session']
        })
        
        cy.loginByForm(testUser.email, testUser.password);
        cy.gotToProject(testUser.project_string_id);
        cy.createLabels(testLabels)
        cy.uploadAndViewSampleImage(testUser.project_string_id);
       
      })

      it('Hides ghost instance info box to ensure out of way for instance templates', () => {
        cy.wait(3000)
        cy.goToStudioFromToolbar()
        cy.get('[data-cy=more_button]').click({force: true});
        cy.wait(100)
        cy.get('[data-cy=advanced_setting]').click({force: true})
        cy.wait(100)
        cy.get('[data-cy=show_ghost_instances]').click({force: true})
      })


      it('Draws a Created Instance Template', () => {
        cy.wait(2000);
        cy.get('[data-cy="instance-type-select"]').click({force: true})
        cy.wait(1000);
        cy.get('.v-list.v-select-list div').contains('instance template 1').click({force: true})
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas(75, 75);

        cy.mousemovecanvas(250, 250);
        cy.mousedowncanvas(250, 250);
        cy.mouseupcanvas(250, 250);

      })
    })

  })

})
