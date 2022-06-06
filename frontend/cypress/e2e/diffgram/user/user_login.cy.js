

describe('Login Flow tests', function () {

  beforeEach(() => {
    cy.visit('http://localhost:8085/')
  })

  it('Should have initial state', ()=>{
    const getStore = () => cy.window().its('app.$store')
    cy.log(getStore())
    getStore().its('state').should('have.all.keys',
      'action',
      'ai',
      'alert',
      'public_project',
      'annotation_state',
      'attribute',
      'project_list',
      'auth',
      'builder_or_trainer',

      'error',
      'job',
      'network',
      'labels',
      'media',
      'input',
      'connection',
      'org',
      'project',
      'user',
      'clipboard',
      'video',
      'ui_schema',
      'snackbar',
      'system'
    );
  })
});
