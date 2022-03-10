
class Balle:

    def __repr__(self):
        return self.val

    def __init__(self, val):
        self.val = str(val)
        self.baller = []

    def add_balle(self, b):
        self.baller.append(b)


hoved_balle = Balle(0)
print(hoved_balle)
print(hoved_balle.baller)
for i in range(10):
    hoved_balle.add_balle(Balle(i+1))
    print(hoved_balle.baller[i].baller)

def baller_i_balle(balle):
    print("Balle nr:", balle.val)
    yield balle
    for b in balle.baller:
        print("INLOOP:", b.val, "balleball:", balle.val)
        yield from baller_i_balle(b)

print(hoved_balle.baller[0].baller)

for b in baller_i_balle(hoved_balle):
    print(b.val)





# FROM OLD IO FILE IN CASE I NEED IT IN FUTURE:
# vim: set expandtab shiftwidth=4 softtabstop=4:


# def open_cmmw(session, stream):
#     """Read an XYZ file from a file-like object.
#
#     Returns the 2-tuple return value expected by the
#     "open command" manager's :py:meth:`run_provider` method.
#     """
#     structures = []
#     atoms = 0
#     bonds = 0
#
#     tmp_atom_dict = {}
#
#     from chimerax.atomic import AtomicStructure
#     s = AtomicStructure(session)
#     residue = s.new_residue("UNK", 'A', 1)  # We place everything in one residue and one structure
#     # TODO maybe have separate structure or residue per chromosome?
#
#     print(type(stream))
#     from chimerax.atomic.struct_edit import add_atom, add_bond
#     from xml.etree import cElementTree as eT
#     from numpy import array, float64
#     root = eT.parse(stream).getroot()
#
#     from VolumePath import markerset
#     marker_sets = markerset.load_marker_set_xml(xml, model_id=s.id)
#
#     for child in root:
#         if(child.tag == "marker"):
#             atoms += 1  # TODO these counters might not be needed because s.num_atoms and s.num_bonds
#             xyz = [child.get("x"), child.get("y"), child.get("z")]
#             tmp_atom_dict[child.get("id")] = add_atom("M", "DNA", residue, array(xyz, dtype=float64))
#             # TODO read and save additional info
#             # TODO add colour
#             pass  # TODO add markers as atoms to structure
#         elif(child.tag == "link"):
#             bonds += 1
#             add_bond(tmp_atom_dict[child.get("id1")], tmp_atom_dict[child.get("id2")], False, )
#             pass  # TODO add links to structure
#         else:
#             pass  # TODO print warning of unsupported line in file.
#
#     structures.append(s)
#
#     status = ("Opened CMMW file containing %d structures (%d atoms, %d bonds)" %
#               (len(structures), atoms, bonds))
#     return structures, status
#


# OLD BEAD SPLIT ALGORITHM
# cut = False
# if(cut):
#     if(int(items[1]) >= bead_start):
#         if(int(items[1]) == bead_start):
#             pass  # Perfect edge alignment -> No cut needed
#         else:
#             # Start edge -> Do cut TODO keep selection in mind
#             # cut = True
#             first_bead, second_bead = cut_bead(session, m, int(items[1]))  # cut before index
#             marker_selection.remove(m)
#             marker_selection.append(second_bead)
#             m = second_bead  # Set the current marker to the new one
#     if(int(items[2]) <= bead_end):
#         if(int(items[2]) == bead_end):
#             pass  # Perfect edge alignment -> No cut needed  # TODO remove this and change if above
#         else:
#             # End edge -> Do cut
#             # cut = True
#             first_bead, second_bead = cut_bead(session, m, int(items[2]))  # cut before index
#             m = second_bead  # Set the current marker to the new one # not necessary


# TODO NB when splitting -> Keep selection? and if dna selection then how, see Note 20/8
# TODO implement option for different representations see Note 20/8

# for i in marker_selection:  # TODO if(not keep_selection)
#     i.selected = True

# OLD COLOUR CODE
# if(len(items) >= 9):
#     # Display colours based on itemRgb items[8]
#     print("Colour")
#     r, g, b = items[8].split(",")
#     print(r, g, b)
#     for i in marker_selection:
#         if i in marker_seen:
#             i.color = np.array([255, 255, 255, 255], dtype=np.ubyte)
#             print("SEEN")
#         else:
#             print("HEPP:)")
#             marker_seen.append(i)  # If a bead has multiple colours just use white
#             i.color = np.array([int(r), int(g), int(b), 255], dtype=np.ubyte)
# elif (len(items) >= 5):
#     # Display greyscale based on score items[4] TODO implement
#     print("Grayscale")
#     pass
# else:
#     print("White")
#     # Display all white
#     for i in marker_selection:
#         i.color = np.array([255, 255, 255, 255], dtype=np.ubyte)


# OLD CODEBLOCK
# TODO NB this is not used and code is outdated:
# def cut_bead(session, bead, pos, keep_original=False):  # TODO keep here or move to different file?
#     '''
#     Split a bead into two new beads while retaining selection and making new bonds.
#     The cut is done before the pos index.
#     :returns: The two new beads
#     '''
#
#     # for var in dir(bead):
#     #     print(var, ":")
#     #     try:
#     #         print(eval("bead." + var))
#     #     except NameError:
#     #         pass
#
#     # TODO Now adding min size change if neccesary
#     minimum_radius = 0.002
#     link_to_marker_ratio = 0.25
#
#     if(len(bead.neighbors) > 2 or len(bead.neighbors) < 1):
#         print("Invalid number of neighbours for bead in cut_bead:", len(bead.neighbors))
#         return None  # TODO or just throw error?
#
#     beadID = re.split(":|-", bead.marker_extra_attributes["beadID"])
#     bead_start = int(beadID[1])
#     bead_end = int(beadID[2])
#
#     # Find radius of new beads
#     print("bead_start:", bead_start, "bead_end:", bead_end)
#     print("pos:", pos, "bead.radius:", bead.radius)
#     print(((pos - bead_start) / (bead_end - bead_start)))
#     print(((bead_end - pos) / (bead_end - bead_start)))  # TODO fix math so radii add up?
#     bead1_radius = ((pos - bead_start) / (bead_end - bead_start)) * bead.radius
#     bead2_radius = ((bead_end - pos) / (bead_end - bead_start)) * bead.radius
#     print("bead1_radius:", bead1_radius)
#     print("bead2_radius:", bead2_radius)
#
#     neighbor_a = bead.neighbors[0]
#     neighbor_b = bead.neighbors[1]
#     neighbor_a_id = re.split(":|-", bead.neighbors[0].marker_extra_attributes["beadID"])
#     neighbor_a_start = int(neighbor_a_id[1])
#
#     # Calculate vector to place beads on
#     vector = None
#     neighbor_first = False
#     string_edge = False
#     if(len(bead.neighbors) == 1):
#         string_edge = True
#         # We are at the end of the string of beads
#         if(neighbor_a_start < bead_start):
#             # neighbour is first -> Vector should point away from neighbour
#             vector = bead.scene_coord - neighbor_a.scene_coord
#             neighbor_first = True
#         else:
#             # neighbour is last -> Vector should point towards neighbour
#             vector = neighbor_a.scene_coord - bead.scene_coord
#
#     else:
#         # We are not at the end of a string of beads
#         if (neighbor_a_start < bead_start):
#             # neighbour_a is first -> Vector should point away from neighbour_a
#             vector = neighbor_b.scene_coord - neighbor_a.scene_coord
#             neighbor_first = True
#         else:
#             # neighbour_a is last -> Vector should point towards neighbour_a
#             vector = neighbor_a.scene_coord - neighbor_b.scene_coord
#
#     # Calculate coordinates of new beads
#     bead_edge = bead.scene_coord - norm_vector(vector) * bead.radius
#     bead1_coord = bead_edge + norm_vector(vector) * bead1_radius
#     bead2_coord = bead_edge + norm_vector(vector) * 2 * bead1_radius + norm_vector(vector) * bead2_radius
#
#
#     from chimerax.markers import MarkerSet
#     from chimerax.markers import create_link
#     marker_sets = session.models.list(type=MarkerSet)
#     m = marker_sets[0]  # TODO this assumes that we are always working on the first one
#
#     if(keep_original):
#         m1 = m.create_marker(bead1_coord, bead.color, max(bead1_radius, minimum_radius))
#     else:
#         m1 = bead  # TODO change size of bonds to neighbors
#         bead.scene_coord = bead1_coord
#         bead.radius = max(bead1_radius, minimum_radius)
#     m2 = m.create_marker(bead2_coord, bead.color, max(bead2_radius, minimum_radius))
#
#     link_radius = max(min(bead1_radius, bead2_radius), minimum_radius) * link_to_marker_ratio
#
#     if(string_edge):
#         if(neighbor_first):
#             if(keep_original):
#                 create_link(neighbor_a, m1, bead.color, link_radius)
#             else:
#                 for b in m1.bonds:
#                     if(b.other_atom(m1) == neighbor_b):
#                         b.delete()
#                         print("REM BOND")
#
#         else:
#             create_link(m2, neighbor_a, bead.color, link_radius)
#             if (not keep_original):
#                 for b in m1.bonds:
#                     if(b.other_atom(m1) == neighbor_a):
#                         b.delete()
#                         print("REM BOND")
#     else:
#         if (neighbor_first):
#             create_link(m2, neighbor_b, bead.color, link_radius)
#             if(keep_original):
#                 create_link(neighbor_a, m1, bead.color, link_radius)
#             else:
#                 for b in m1.bonds:
#                     if(b.other_atom(m1) == neighbor_b):
#                         b.delete()
#                         print("REM BOND")
#
#         else:
#             create_link(m2, neighbor_a, bead.color, link_radius)
#             if(keep_original):
#                 create_link(neighbor_b, m1, bead.color, link_radius)
#             else:
#                 for b in m1.bonds:
#                     if(b.other_atom(m1) == neighbor_a):
#                         b.delete()
#                         print("REM BOND")
#     create_link(m1, m2, bead.color, link_radius)
#
#
#     # Set extra_marker_attributes
#     m1.marker_extra_attributes = {"chrID": bead.marker_extra_attributes["chrID"],
#                                   "beadID": beadID[0] + ":" + str(bead_start) + "-" + str(pos)}
#     m2.marker_extra_attributes = {"chrID": bead.marker_extra_attributes["chrID"],
#                                   "beadID": beadID[0] + ":" + str(pos) + "-" + str(bead_end)}
#     # Delete old bead  # We change the original to be part of the split instead since deletion breaks indexing
#     # if(not keep_original):
#     #     for b in bead.bonds:
#     #         b.delete()
#     #     bead.delete()
#     # TODO preserve selection option
#
#     return m1, m2

# TODO Not necessary anymore as has been implemented in ChimeraX by default
# def save_marker_attributes(session, model_id):  # TODO must apply to submodels as well!
#     m_sets = session.models.list(type=MarkerSet)
#     print(m_sets)
#     for m_set in m_sets:
#         if (m_set.id_string == model_id):
#             if(hasattr(m_set, "save_marker_attribute_in_sessions")):
#                 m_set.save_marker_attribute_in_sessions('marker_extra_attributes', Dict)
#             else:  # Backwards compatibility
#                 from chimerax.atomic import Atom
#                 Atom.register_attr(session, 'marker_extra_attributes', "markers", attr_type=Dict)
#             print("SUCCESS")
#
#
# save_marker_attributes_desc = CmdDesc(required=[("model_id", StringArg)])