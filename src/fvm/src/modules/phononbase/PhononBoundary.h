// This file os part of FVM
// Copyright (c) 2012 FVM Authors
// See LICENSE file for terms.

#ifndef _PHONONBOUNDARY_H_
#define _PHONONBOUNDARY_H_

#include "Mesh.h"
#include <math.h>
#include "NumType.h"
#include "Array.h"
#include "Vector.h"
#include "Field.h"
#include "StorageSite.h"
#include "CRConnectivity.h"
#include "MultiFieldMatrix.h"
#include "CRMatrix.h"
#include "FluxJacobianMatrix.h"
#include "DiagonalMatrix.h"
#include "GeomFields.h"
#include "pmode.h"
#include "Kspace.h"
#include "kvol.h"

template<class X>
class PhononBoundary
{
 public :
  
  typedef typename NumTypeTraits<X>::T_Scalar T_Scalar;

  typedef Array<int> IntArray;
  
  typedef Array<T_Scalar> TArray;
  typedef Vector<T_Scalar,3> VectorT3;  
  typedef Array<VectorT3> VectorT3Array;

  typedef Array<X> XArray;
  typedef Vector<X,3> VectorX3; //also needed for phonons
  typedef Array<VectorX3> VectorX3Array;
  typedef Kspace<X> Xkspace;
  typedef kvol<X> Xkvol;
  typedef pmode<X> Xmode;
  typedef typename Xmode::Refl_pair Refl_pair;
  
 PhononBoundary(const StorageSite& faces,
		const Mesh& mesh,
		const GeomFields& geomFields,
		const Xkspace& kspace,
		PhononModelOptions<X>& opts,
		const int fg_id):
  
  _faces(faces),
    _cells(mesh.getCells()),
    _ibType(dynamic_cast<const IntArray&>(geomFields.ibType[_cells])), 
    _faceCells(mesh.getFaceCells(_faces)),
    _areaMagField(geomFields.areaMag),
    _faceAreaMag(dynamic_cast<const TArray&>(_areaMagField[_faces])),
    _areaField(geomFields.area),
    _faceArea(dynamic_cast<const VectorT3Array&>(_areaField[_faces])),
    _options(opts),
    _kspace(kspace), 
    _fg_id(fg_id)
  {}

  PhononModelOptions<X>&   getOptions() {return _options;}  

  void applyReflectingWall(int f,const X refl) const
  {
    
    const int c0 = _faceCells(f,0);
    const int c1 = _faceCells(f,1); ///changed
    X tot_in = 0.;  //total incoming energy (to wall)
    X tot_dk3 = 0.; //total weight of incoming energy
    
    if (_ibType[c0] != Mesh::IBTYPE_FLUID)
      return;

    // sum up energy incoming to boundary (from domain)
    int numK=_kspace.getlength();
    for (int k=0;k<numK;k++)
      {

	Xkvol& kv=_kspace.getkvol(k);
	X dk3=kv.getdk3();
	int numM=kv.getmodenum();

	for (int m=0;m<numM;m++) //mode loop beg
	  {
	    
	    Xmode& mode=kv.getmode(m);
	    Field& efield=mode.getfield();
	    VectorT3 vg = mode.getv();     // phonon group velocity
	    XArray& e_val = dynamic_cast< XArray&>(efield[_cells]);  // e"
	    const VectorT3 en = _faceArea[f]/_faceAreaMag[f];  //normal unit vector to face
	    const VectorT3 sn = vg/sqrt(pow(vg[0],2)+pow(vg[1],2)+pow(vg[2],2));
	    const X sn_dot_en = sn[0]*en[0]+sn[1]*en[1]+sn[2]*en[2];
	    const X vg_dot_en = vg[0]*en[0]+vg[1]*en[1]+vg[2]*en[2];
  
	    if (sn_dot_en > T_Scalar(0.0))
	      {
		tot_in+=e_val[c0]*dk3*vg_dot_en;
		tot_dk3+=vg_dot_en*dk3;
	      }
	    else
	      {
		e_val[c1]=0.;
	      }

	  } //mode loop end	
      }

    const X diff_refl = tot_in/tot_dk3; // value for e" leaving the wall

    // assign values for incoming (upwinded) and outgoing (reflected) to/from wall
    for (int k=0;k<numK;k++)
      {
	
	Xkvol& kv=_kspace.getkvol(k);
	int numM=kv.getmodenum();

	for (int m=0;m<numM;m++) //mode loop beg
	  {
	    
	    Xmode& mode=kv.getmode(m);
	    Field& efield=mode.getfield();
	    VectorT3 vg = mode.getv();     // phonon group velocity
	    XArray& e_val = dynamic_cast<XArray&>(efield[_cells]);  // e"
	    const VectorT3 en = _faceArea[f]/_faceAreaMag[f];  //normal unit vector to face
	    const X vg_dot_en = vg[0]*en[0]+vg[1]*en[1]+vg[2]*en[2];
	    
	    if (vg_dot_en > T_Scalar(0.0))
	      {
		
		Refl_pair& rpairs=mode.getReflpair(_fg_id);
		//X w1=rpairs.first.first;
		//X w2=rpairs.second.first;
		int k1=rpairs.first.second;
		//int k2=rpairs.second.second;
		Xmode& mode1=_kspace.getkvol(k1).getmode(m);
		//Xmode& mode2=_kspace.getkvol(k2).getmode(m);
		Field& field1=mode1.getfield();
		//Field& field2=mode2.getfield();
		XArray& e_val1=dynamic_cast<XArray&>(field1[_cells]);
		//XArray& e_val2=dynamic_cast<XArray&>(field2[_cells]);
		e_val1[c1]+=refl*e_val[c0];
		//e_val2[c1]+=refl*w2*e_val[c0];
		e_val[c1]=e_val[c0];    // upwinded value
	      }
	    else
	      {
		e_val[c1]+=(1-refl)*diff_refl;  // diffusely reflected value
	      }
	  } //mode loop end	
      }
  }

 void applyReflectingWall(FloatValEvaluator<X>& bRefl) const
  {
    for (int i=0; i<_faces.getCount();i++)
      applyReflectingWall(i,bRefl[i]);
  }


 void applyTemperatureWall(int f,const X Twall) const
  {
    
    const int c0 = _faceCells(f,0);
    const int c1 = _faceCells(f,1); ///changed
    
    if (_ibType[c0] != Mesh::IBTYPE_FLUID)
      return;

    // sum up energy incoming to boundary (from domain)
    int numK=_kspace.getlength();
 
    for (int k=0;k<numK;k++)
      {
	Xkvol& kv=_kspace.getkvol(k);
	int numM=kv.getmodenum();
     
	for (int m=0;m<numM;m++) //mode loop beg
	  {
	    Xmode& mode=kv.getmode(m);
	    Field& efield=mode.getfield();
	    VectorX3 vg = mode.getv();
	    XArray& e_val = dynamic_cast< XArray&>(efield[_cells]);  // e"
	    const VectorX3 en = _faceArea[f]/_faceAreaMag[f];  //normal unit vector to face
	    const X vg_dot_en = vg[0]*en[0]+vg[1]*en[1]+vg[2]*en[2];
	    	          
	    if (vg_dot_en > T_Scalar(0.0))
	      {
		e_val[c1]=e_val[c0];
	      }
	    else
	      {
		e_val[c1]=mode.calce0(Twall);
	      }
	    
	  } //mode loop end	
      }
  }

 void applyTemperatureWall(FloatValEvaluator<X>& bTemp) const
  {
    for (int j=0; j<_faces.getCount();j++)
      {
	applyTemperatureWall(j,bTemp[j]);
      }
  }


 /*


 void applyInterfaceCondition(int f,const X refl, const X trans) const
  {
    
    const int c0 = _faceCells(f,0);
    const int c1 = _faceCells(f,1);
    T_Scalar sign(NumTypeTraits<T_Scalar>::getUnity());
    if (c1 < _cells.getSelfCount())
       { 
	 // c0 is ghost cell and c1 is boundry cell, so swap cell numbers
	 // so that c1p refers to the ghost cell in the following
	 int temp = c0;
	 c0 = c1;
	 c1 = temp;
	 sign *= -1.0;
       }


    X tot_in = 0.;  //total incoming energy (to wall)
    X tot_dk3 = 0.; //total weight of incoming energy
    
    if (_ibType[c0] != Mesh::IBTYPE_FLUID)
      return;

    // sum up energy incoming to boundary (from domain)
    int numK=_kspace.getlength();
    for (int k=0;k<numK;k++)
      {

	Xkvol& kv=_kspace.getkvol(k);
	X dk3=kv.getdk3();
	int numM=kv.getmodenum();

	for (int m=0;m<numM;m++) //mode loop beg
	  {
	    
	    Xmode& mode=kv.getmode(m);
	    Field& efield=mode.getfield();
	    VectorT3 vg = mode.getv();     // phonon group velocity
	    XArray& e_val = dynamic_cast< XArray&>(efield[_cells]);  // e"
	    const VectorT3 en = sign*(_faceArea[f]/_faceAreaMag[f]);  //outward normal unit vector to face
	    const VectorT3 sn = vg/sqrt(pow(vg[0],2)+pow(vg[1],2)+pow(vg[2],2));
	    const X sn_dot_en = sn[0]*en[0]+sn[1]*en[1]+sn[2]*en[2];
	    const X vg_dot_en = vg[0]*en[0]+vg[1]*en[1]+vg[2]*en[2];
  
	    if (sn_dot_en > T_Scalar(0.0))
	      {
		tot_in+=e_val[c0]*dk3*vg_dot_en;
		tot_dk3+=vg_dot_en*dk3;
	      }
	    else
	      {
		//e_val[c1]=0.;
	      }

	  } //mode loop end	
      }

    const X diff_refl = tot_in/tot_dk3; // value for e" leaving the wall

    // assign values for incoming (upwinded) and outgoing (reflected) to/from wall
    for (int k=0;k<numK;k++)
      {
	
	Xkvol& kv=_kspace.getkvol(k);
	int numM=kv.getmodenum();

	for (int m=0;m<numM;m++) //mode loop beg
	  {
	    
	    Xmode& mode=kv.getmode(m);
	    Field& efield=mode.getfield();
	    VectorT3 vg = mode.getv();     // phonon group velocity
	    XArray& e_val = dynamic_cast<XArray&>(efield[_cells]);  // e"
	    const VectorT3 en = sign*(_faceArea[f]/_faceAreaMag[f]);  //normal unit vector to face
	    const X vg_dot_en = vg[0]*en[0]+vg[1]*en[1]+vg[2]*en[2];
	    
	    if (vg_dot_en > T_Scalar(0.0))
	      {
		
		Refl_pair& rpairs=mode.getReflpair(_fg_id);
		X w1=rpairs.first.first;
		X w2=rpairs.second.first;
		int k1=rpairs.first.second;
		int k2=rpairs.second.second;
		Xmode& mode1=_kspace.getkvol(k1).getmode(m);
		Xmode& mode2=_kspace.getkvol(k2).getmode(m);
		Field& field1=mode1.getfield();
		Field& field2=mode2.getfield();
		XArray& e_val1=dynamic_cast<XArray&>(field1[_cells]);
		XArray& e_val2=dynamic_cast<XArray&>(field2[_cells]);
		e_val1[c1]+=refl*w1*e_val[c0];
		e_val2[c1]+=refl*w2*e_val[c0];
		e_val[c1]=e_val[c0];    // upwinded value
	      }
	    else
	      {
		e_val[c1]=refl*diff_refl;  // diffusely reflected value
	      }
	  } //mode loop end	
      }
  }

 void applyInterfaceCondition(FloatValEvaluator<X>& bRefl, FloatValEvaluator<X>& bTrans) const
  {
    for (int i=0; i<_faces.getCount();i++)
      applyInterfaceCondition(i,bRefl[i],bTrans[i]);
  }
*/
 /*
 
  void applyZeroGradientBC(int f) const
  {
    const int c0 = _faceCells(f,0);
    const int c1 = _faceCells(f,1);
    
    if (_ibType[c0] != Mesh::IBTYPE_FLUID)
      return;
    
    const int numDirections = _quadrature.getDirCount();
    
    for (int j=0; j<numDirections; j++)
      {
	Field& fnd = *_dsfPtr.dsf[j];
	XArray& dsf = dynamic_cast< XArray&>(fnd[_cells]);
	dsf[c1]=dsf[c0];
      }
  }
  void applyZeroGradientBC() const
  {
    for (int i=0; i<_faces.getCount();i++)
      applyZeroGradientBC(i);
  } 
    */

  
 protected:

  const StorageSite& _faces;
  const StorageSite& _cells;
  const Array<int>& _ibType;
  const CRConnectivity& _faceCells;
  const Field& _areaMagField;
  const TArray& _faceAreaMag;
  const Field& _areaField;
  const VectorT3Array& _faceArea;
  PhononModelOptions<X>& _options;
  const Xkspace& _kspace;
  const int _fg_id;
};
  
#endif
