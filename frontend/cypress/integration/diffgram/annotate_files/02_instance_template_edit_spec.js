import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";


describe('Instance Template Creation', () => {

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

    const template_name = 'instance template for edit';
    const nodes = [{x: 100, y: 100}, {x: 300, y: 300}, {x: 400, y: 400}, {x: 75, y: 150}];

    it('Creates Instance Template For Purpose Of Editing in Next Step', () => {
      cy.createInstanceTemplate(template_name, {
        nodes: nodes,
        edges: [[0, 1], [0, 2], [0, 3]],
      });
      cy.wait(5000);
    })

    it('Edits Instance Template Name', () => {
      cy.get('[data-cy=instance_template_name_text_field]').type('{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}');
    })

    it('Edits Instance Template Nodes', () => {
      cy.get('[data-cy=edit_toggle_instance_template_create]').click({force: true});
      cy.get('[data-cy=instance_template_name_text_field]').type('{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}');
      cy.mousemovecanvas(nodes[0].x, nodes[0].y);
      cy.dragcanvas(nodes[0].x, nodes[0].y, nodes[0].x + 85, nodes[0].y);


    })

    it('Edits Instance Draw Mode', () => {
      cy.get('[data-cy=guided_mode_button]').click({force: true});
      cy.get('[data-cy=1_click_mode_button]').click({force: true});
    })

    it('Edits Ordering of Nodes', () => {
      cy.get('[data-cy=node-ordering-button]').click()
      .get('[data-cy=node-item-1]').drag('[data-cy=node-item-3]')
      cy.get('[data-cy=save_order_button]').click({force: true})
        .window().then(window => {
          let component = window.InstanceTemplateDialog
          let node_1 = component.instance.nodes.find(n => n.name === '2')
          expect(node_1.ordinal).to.eq(4);
        })
    })

    it('Changes Color of a Node', () => {
      cy.get('[data-cy=select-color]').click({force: true})
        .get('#color-picker-instance-template > div.vc-chrome-body > div.vc-chrome-fields-wrap > div:nth-child(1) > div > div > input')
        .click({force: true})
        .get('#color-picker-instance-template > div.vc-chrome-body > div.vc-chrome-fields-wrap > div:nth-child(1) > div > div > input')
        .type('{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}{backspace}#FF0000')
        .get('[data-cy=1_click_mode_button]').click({force: true})
        .get('[data-cy=activate-coloring-button]').click({force: true})
        .get('[data-cy=activate-coloring-button]').click({force: true})
        .mousedowncanvas(nodes[0].x, nodes[0].y)
        .mouseupcanvas(nodes[0].x, nodes[0].y)
        .mouseupcanvas(0, 0)
        .window().then(window => {
          let component = window.InstanceTemplateDialog
          let node_1 = component.instance.nodes.find(n => n.name === '1')
          cy.log(component.instance)
          expect(node_1.color.hex).to.eq('#FF0000');
        })
    })

    it('Saves the edited instance template', () =>{
      cy.get('[data-cy=save_instance_template_button]').click({force: true});
    })
  })

})
