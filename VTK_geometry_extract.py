import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

def VTKextractInfo(VTKfile):
  # Set file reader
  reader = None
  if input[len(input)-3:] == "vtk":
    reader = vtk.vtkUnstructuredGridReader()
  elif input[len(input)-3:] == "vtu":
    reader = vtk.vtkXMLUnstructuredGridReader()
  else:
    print("Undefined file type")
    exit()

  reader.SetFileName(input)
  reader.Update()
  data = reader.GetOutput()
  # extract node & connectivity info
  node = vtk_to_numpy(data.GetPoints().GetData())
  element = []
  cells = data.GetCells()
  for ic in range(cells.GetNumberOfCells()):
    cell = vtk.vtkIdList()
    cells.GetCellAtId(ic,cell)
    pointsInCell = []
    for j in range(cell.GetNumberOfIds()):
      pointsInCell.append(cell.GetId(j))
    element.append(pointsInCell)
  # Output
  np.savetxt("node.dat",node)
  np.savetxt("element.dat",element)

if(__name__ == "__main__"):
  input = "test.vtk"
  VTKextractInfo(input)