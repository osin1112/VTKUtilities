############################################################################################
# surface data (.stl) -> volume mesh (structured grid (.vtk))
# Dependency: VTK ($ pip install vtk pyevtk).
# Reference:  https://qiita.com/dwatanabee/items/b938b46ef911a43b92ba
############################################################################################

import numpy as np
import vtk
import vtk.util.numpy_support as vnp

######################## File path & parameters for quality of mesh ########################
iFile = "sample.stl"
oFile = "test.vtk"
fineness = 70
tolerance = 1e-7 # range: 1e-7 ~ 1e-3
############################################################################################

reader = vtk.vtkSTLReader()
reader.SetFileName(iFile)
reader.Update()
surface = reader.GetOutput()
bounds = surface.GetBounds()
max_size = max([bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]])
cell_dims = [fineness, fineness, fineness]
mesh_pitch = [max_size/cell_dims[0], max_size/cell_dims[1], max_size/cell_dims[2]]
mins = [bounds[0], bounds[2], bounds[4]]
px, py, pz = mesh_pitch
mx, my, mz = (cell_dims+np.array([1, 1, 1])) * mesh_pitch 
points = vtk.vtkPoints()
coords = np.stack(np.mgrid[:mx:px, :my:py, :mz:pz], -1).reshape(-1, 3) + mins
points.SetData(vnp.numpy_to_vtk(coords))
structured_base_mesh = vtk.vtkStructuredGrid()
structured_base_mesh.SetExtent(0, cell_dims[0], 0, cell_dims[1], 0, cell_dims[2])
structured_base_mesh.SetPoints(points)
append = vtk.vtkAppendFilter()
append.AddInputData(structured_base_mesh)
append.Update()
base_mesh = append.GetOutput()
cell_centers = vtk.vtkCellCenters()
cell_centers.SetInputData(base_mesh)
cell_centers.Update()
poly_points = cell_centers.GetOutput()
select_enclosed = vtk.vtkSelectEnclosedPoints()
select_enclosed.SetInputData(poly_points)
select_enclosed.SetSurfaceData(surface)
select_enclosed.SetTolerance(tolerance)
select_enclosed.Update()
isInsideOrOutside = select_enclosed.GetOutput().GetPointData().GetArray("SelectedPoints")
structured_base_mesh.GetCellData().AddArray(isInsideOrOutside)
threshold = vtk.vtkThreshold()
threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "SelectedPoints")
threshold.SetInputData(structured_base_mesh)
threshold.SetLowerThreshold(1)
threshold.SetUpperThreshold(1)
threshold.Update()
writer = vtk.vtkDataSetWriter()
writer.SetFileName(oFile)
writer.SetInputData(threshold.GetOutput())
writer.Update()