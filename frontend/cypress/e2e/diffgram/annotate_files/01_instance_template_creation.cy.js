import testUser from '../../../fixtures/users.json';

describe('Instance Template Creation', () => {

  context('Instance Templates Creation', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);

    })

    it('Creates Instance Template', () => {
      cy.createInstanceTemplate('instance template 1', {
        nodes: [{x: 100, y: 100}, {x: 300, y: 300}, {x: 400, y: 400}, {x: 75, y: 150}],
        edges: [[0, 1], [0, 2], [0, 3]],
      });
      cy.get('[data-cy=save_instance_template_button]').click({force: true});
      cy.wait(5000);
    })
  })
})
