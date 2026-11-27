# Stage 02 Proof Notes

These notes justify the implementation in `src/renewable_routing/`. The flow,
residual-capacity, and max-flow/min-cut arguments follow
`Uploaded_Lecture07_graph_theory_advanced.pdf`, PDF pages 123-142. The
Edmonds-Karp argument follows PDF pages 150-155. Deterministic adjacency order,
edge-ID-carrying residual arcs, and full residual reconstruction are repository
implementation choices specified by Stage 02.

## Feasible initialization

Every supported original edge has lower capacity zero, so assigning zero to
every edge respects all bounds. Every node then has zero outflow and zero
inflow. Thus all intermediate nodes satisfy conservation and the source and
sink both have flow value zero.

## Preservation under augmentation

For an original edge with capacity `c` and flow `f`, a forward residual arc has
capacity `c - f`; increasing `f` by at most that amount cannot exceed `c`. A
reverse residual arc has capacity `f`; decreasing `f` by at most that amount
cannot make it negative. Residual arcs retain the original edge ID and
direction, so this update remains valid for parallel and opposite-direction
original edges.

At each internal vertex on a simple augmenting path, one incident residual step
enters and one leaves. Considering forward increases and reverse decreases in
the original network, their combined effect on `outflow - inflow` is zero.
Therefore conservation is preserved. This is the invariant; individual
incoming or outgoing original-edge flows may decrease during cancellation.

## Positive progress and termination

The bottleneck is the minimum positive residual capacity on the path, so it is
positive. The first path step changes source net outflow by the bottleneck, and
the last changes sink net outflow by its negative. Hence each augmentation
increases the flow value by exactly the bottleneck.

All capacities and flows are integers. Every bottleneck is therefore an integer
of at least one. The value is bounded by the total original capacity leaving
the source, so Ford-Fulkerson performs at most that many augmentations and
terminates. This is the integer-capacity argument from Lecture 7, PDF pages
135-137.

## Equal-capacity cut certificate

When no residual source-to-sink path remains, let `S` be the vertices reachable
from the source through positive residual arcs and let `T` be every other
vertex. The sink is in `T`. Every original edge from `S` to `T` is saturated;
otherwise its forward residual arc would make its target reachable. Every
original edge from `T` to `S` has zero flow; otherwise its reverse residual arc
would make its source reachable.

Consequently, source net outflow equals the sum of capacities on original edges
from `S` to `T`. This is the cut capacity. Every feasible flow is bounded above
by every source/sink cut, so a feasible flow equal to this cut is maximum. The
implementation recomputes both feasibility and cut capacity from original
edges before returning a result. Reverse residual arcs are not counted in the
certificate. This follows Lecture 7, PDF pages 138-142.

## Edmonds-Karp augmentation bound

Edmonds-Karp chooses a residual path with the fewest edges by BFS. Its residual
distance from the source to any vertex does not decrease after augmentation.
When an arc is critical, meaning it attains the path bottleneck and disappears,
that same directed residual arc can become critical again only after its
opposite residual direction participates in a later path. The BFS levels then
force the tail's source distance to increase by at least two. Each directed
arc can therefore be critical only `O(n)` times, and at least one path arc is
critical per augmentation. Across `O(m)` residual directions this gives
`O(n*m)` augmentations and the familiar `O(n*m^2)` adjacency-search bound
described on Lecture 7 PDF pages 151-155.

This implementation additionally rebuilds and validates an `O(n + m)` residual
snapshot on every iteration. With `A` successful augmentations, its direct
accounting is `O((A + 1) * (n + m))` time and `O(n + m)` working memory. For
Edmonds-Karp, substituting `A = O(n*m)` gives the conservative
`O((n*m + 1) * (n + m))` bound. These maximum-flow algorithms do not optimize
cost and do not count as the assignment's classical minimum-cost-flow methods.
