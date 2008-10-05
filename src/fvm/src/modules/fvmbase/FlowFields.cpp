#include "FlowFields.h"

FlowFields::FlowFields(const string baseName) :
  velocity(baseName + ".velocity"),
  pressure(baseName + ".pressure"),
  massFlux(baseName + ".massFlux"),
  velocityGradient(baseName + ".velocityGradient"),
  pressureGradient(baseName + ".pressureGradient"),
  momentumFlux(baseName + ".momentumFlux"),
  viscosity(baseName + ".viscosity"),
  density(baseName + ".density"),
  continuityResidual(baseName + ".continuityResidual")
{}

