from dataclasses import dataclass
import itertools


vertex_id = None


@dataclass(slots=True)
class Vertex:
	v: int
	id: int
	next: 'Vertex'

	def __iter__(self):
		yield self
		vertex = self.next
		while vertex.v != self.v:
			yield vertex
			vertex = vertex.next

	def triangulate(self):
		base_v = self.next
		cur_v = base_v.next.next
		while cur_v.v != self.v:
			yield base_v.v, cur_v.v
			cur_v = cur_v.next

	def __repr__(self):
		return f"{self.__class__.__name__}(v={self.v}, id={self.id}" \
		       f", next={self.__class__.__name__}(v={self.next.v}, id={self.next.id}))"

	__str__ = __repr__


Polygons_T = list[Vertex]
Clones_T = dict[int, Vertex]
Relatives_T = tuple[Clones_T, ...]


def init_polygon(n: int) -> tuple[Polygons_T, Relatives_T]:
	"""Init polygon with n vertices."""
	last = Vertex(n-1, n-1, None)
	vertex = last
	for i in reversed(range(n-1)):
		vertex = Vertex(i, i, vertex)
	last.next = vertex
	global vertex_id
	vertex_id = itertools.count(n)
	return [last], tuple({0: vertex} for vertex in last.next)


def get_polygon_to_cut(
	i: int,
	j: int,
	relatives: Relatives_T
) -> int:
	"""Get index of polygon to cut by indices of initial vertices."""
	if len(relatives[i]) < len(relatives[j]):
		r1, r2 = relatives[i], relatives[j]
	else:
		r1, r2 = relatives[j], relatives[i]

	for pi in r1:
		if pi in r2:
			return pi
	else:
		# Should never happen
		raise ValueError("Implementation error: no shared polygon")


def do_cut(i: int, j: int, polygons: Polygons_T, relatives: Relatives_T) -> None:
	"""Do cut between i-th and j-th initial vertices."""
	pi = get_polygon_to_cut(i, j, relatives)
	v1, v2 = relatives[i][pi], relatives[j][pi]

	# Ensure that v2->v1 length <= v1->v2 length.
	for u1, u2 in zip(v1, v2):
		if u1.next.v == i:
			v1, v2 = v2, v1
			break
		if u2.next.v == j:
			break

	v1_next, v2_next = Vertex(v2.v, next(vertex_id), v2.next), Vertex(v1.v, next(vertex_id), v1.next)
	v1.next, v2.next = v1_next, v2_next

	polygons[pi] = v1
	polygons.append(v2)
	new_pi = len(polygons) - 1
	relatives[i][new_pi], relatives[j][new_pi] = v2_next, v1_next
	v = v2.next
	while v.v != v2_next.v:
		relatives[v.v][new_pi] = relatives[v.v].pop(pi)


def polygon_str(vertex: Vertex) -> str:
	return "->".join(str(cv.v) for cv in vertex)


def show_polygons(polygons: Polygons_T) -> None:
	print("\n".join(polygon_str(vertex) for vertex in polygons))


def main():
	n = int(input())
	k = int(input())

	# polygons[i] is one of the vertices of i-th polygon.
	# relatives[i] is dict with indices of polygons i-th initial vertex belongs
	# to as keys and respective 'clones' of i-th initial vertex as values.
	polygons, relatives = init_polygon(n)

	for _ in range(k):
		i, j = map(int, input().split())
		do_cut(i, j, polygons, relatives)

	cuts = tuple(
		itertools.chain.from_iterable(
			vertex.triangulate()
			for vertex in polygons
		)
	)
	print(len(cuts))
	for (i, j) in cuts:
		print(i, j)


if __name__ == "__main__":
	main()
