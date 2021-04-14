


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
      'annotation_assignment',
      'annotation_project',
      'annotation_state',
      'attribute',
      'auth',
      'builder_or_trainer',
      'error',
      'job',
      'labels',
      'media',
      'input',
      'connection',
      'org',
      'project',
      'user',
      'video');
  })
});
