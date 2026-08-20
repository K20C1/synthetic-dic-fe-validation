[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [file]
    type = FileMeshGenerator
    file = DogBoneSample.msh
  []
[]

[Physics/SolidMechanics/QuasiStatic]
  [all]
    strain = SMALL
    add_variables = true
    generate_output = 'vonmises_stress strain_yy stress_yy'
  []
[]

[Functions]
  [ramp]
    type = PiecewiseLinear
    x = '0 1'
    y = '0 20'   # mm end displacement. Elastic verification run; magnitude arbitrary within elastic range.
  []
[]

[BCs]
  [fix_x]
    type = DirichletBC
    variable = disp_x
    boundary = grip_fixed
    value = 0
  []
  [fix_y]
    type = DirichletBC
    variable = disp_y
    boundary = grip_fixed
    value = 0
  []
  [fix_z]
    type = DirichletBC
    variable = disp_z
    boundary = grip_fixed
    value = 0
  []
  [pull_y]
    type = FunctionDirichletBC
    variable = disp_y
    boundary = grip_loaded
    function = ramp
  []
[]

[Materials]
  [elasticity]
    type = ComputeIsotropicElasticityTensor
    youngs_modulus = 200000   # MPa, AISI 316
    poissons_ratio = 0.28
  []
  [stress]
    type = ComputeLinearElasticStress
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  end_time = 1
  dt = 0.1
[]

[Outputs]
  exodus = true
[]