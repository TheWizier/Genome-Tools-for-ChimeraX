
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