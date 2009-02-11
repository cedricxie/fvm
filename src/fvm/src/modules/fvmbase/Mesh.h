#ifndef _MESH_H_
#define _MESH_H_

#include "Array.h"

#include "StorageSite.h"
#include "Vector.h"
#include "Field.h"
#include "FieldLabel.h"

class CRConnectivity;

struct FaceGroup
{
  FaceGroup(const int count_,
            const int offset_,
            const StorageSite& parent_,
            const int id_,
            const string& groupType_) :
    site(count_,0,offset_,&parent_),
    id(id_),
    groupType(groupType_)
  {}
  
  const StorageSite site;
  const int id;
  const string groupType;
};

typedef shared_ptr<FaceGroup> FaceGroupPtr; 
typedef vector<FaceGroupPtr> FaceGroupList;  

class Mesh 
{
public:

  typedef Vector<double,3> VecD3;
  
  typedef pair<const StorageSite*, const StorageSite*> SSPair;
  typedef map<SSPair,shared_ptr<CRConnectivity> > ConnectivityMap;
  enum
    {
      CELL_BAR2,
      CELL_TRI3,
      CELL_QUAD4,
      CELL_TETRA4,
      CELL_HEX8,
      CELL_PYRAMID,
      CELL_PRISM,
      CELL_TYPE_MAX
    } CellType;
  

  enum
    {
      IBTYPE_FLUID,
      IBTYPE_SOLID,
      IBTYPE_BOUNDARY
    };
  
  Mesh(const int dimension, const int id);
  
  ~Mesh();

  DEFINE_TYPENAME("Mesh");

  int getDimension() const {return _dimension;}
  int getID() const {return _id;}
  
  const StorageSite& getFaces() const {return _faces;}
  const StorageSite& getCells() const {return _cells;}
  const StorageSite& getNodes() const {return _nodes;}

  StorageSite& getFaces() {return _faces;}
  StorageSite& getCells() {return _cells;}
  StorageSite& getNodes() {return _nodes;}

  //  const CRConnectivity& getConnectivity(const StorageSite& from,
  //                                      const StorageSite& to) const;

  const CRConnectivity& getAllFaceNodes() const;
  const CRConnectivity& getAllFaceCells() const;
  const CRConnectivity& getCellNodes() const;
  
  const CRConnectivity& getFaceCells(const StorageSite& site) const;
  const CRConnectivity& getFaceNodes(const StorageSite& site) const;
  const CRConnectivity& getCellFaces() const;
  const CRConnectivity& getCellCells() const;

  //const Array<int>& getCellTypes() const;
  //const Array<int>& getCellTypeCount() const;

  const FaceGroup& getInteriorFaceGroup() const {return *_interiorFaceGroup;}
  
  int getFaceGroupCount() const {return _faceGroups.size();}
  int getBoundaryGroupCount() const {return _boundaryGroups.size();}
  int getInterfaceGroupCount() const {return _interfaceGroups.size();}

  const FaceGroupList& getBoundaryFaceGroups() const
  {return _boundaryGroups;}

#if 0
  const FaceGroup&
  getFaceGroup(const int i) const {return *_faceGroups[i];}

  const FaceGroup&
  getBoundaryGroup(const int i) const {return *_boundaryGroups[i];}

  const FaceGroup&
  getInterfaceGroup(const int i) const {return *_interfaceGroups[i];}
#endif

  const StorageSite& createInteriorFaceGroup(const int size);
  const StorageSite& createInterfaceGroup(const int size,const int offset, 
                                    const int id);
  const StorageSite& createBoundaryFaceGroup(const int size, const int offset, 
                                       const int id, const string& boundaryType);

  void setCoordinates(shared_ptr<Array<VecD3> > x) {_coordinates = x;}
  void setFaceNodes(shared_ptr<CRConnectivity> faceNodes);
  void setFaceCells(shared_ptr<CRConnectivity> faceCells);

  void setConnectivity(const StorageSite& rowSite, const StorageSite& colSite,
                       shared_ptr<CRConnectivity> conn)
  {
    SSPair key(&rowSite,&colSite);
    _connectivityMap[key] = conn;
  }

  const Array<VecD3>& getNodeCoordinates() const {return *_coordinates;}
  ArrayBase* getNodeCoordinates() {return &(*_coordinates);}

  const Array<int>& getIBType() const;

  int getIBTypeForCell(const int c) const;
  
  void setIBTypeForCell(const int c, const int type);

  VecD3 getCellCoordinate(const int c) const;
  //Array<int>& getIBType();
  
protected:
  const int _dimension;
  const int _id;
  
  StorageSite _cells;
  StorageSite _faces;
  StorageSite _nodes;
  shared_ptr<FaceGroup> _interiorFaceGroup;
  FaceGroupList _faceGroups;
  FaceGroupList _boundaryGroups;
  FaceGroupList _interfaceGroups;
  mutable ConnectivityMap _connectivityMap;
  shared_ptr<Array<VecD3> > _coordinates;

  mutable shared_ptr<Array<int> > _ibType;

  Array<int>& getOrCreateIBType() const;
  
  //mutable Array<int> *_cellTypes;
  //mutable Array<int> *_cellTypeCount;
};

typedef vector<Mesh*> MeshList;

#endif
