#ifndef _FLOWFIELDS_H_
#define _FLOWFIELDS_H_


#include "Field.h"

struct FlowFields
{
  FlowFields(const string baseName);

  Field velocity;
  Field pressure;
  Field massFlux;
  Field velocityGradient;
  Field pressureGradient;
  Field momentumFlux;
  Field viscosity;
  Field density;
  Field continuityResidual;
};

#endif
