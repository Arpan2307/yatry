from yatry.utils.models.tree import Tree
from yatry.utils.models import Passenger
from yatry.utils.optim.route import find_route
from yatry.utils.data.locations import Location
from yatry.utils.models.symm_dict import SymmetricKeyDict


type RoadRegistry = SymmetricKeyDict[Location, float]
type MapNode = Tree[Location]


class Map:
    """
    Implements a map with locations and roads.

    The map here is implemented as a tree instead of a graph to avoid multiple
    paths between locations to reduce complexity of optimization.

    Attributes:
        _roads (RoadRegistry): A symmetric dictionary with locations as keys
            and the fare as the value.
        _root (Tree[Location]): The root location of the map. This should be the
            primary point of focus in the region.
        _locations (dict[Location, MapNode]): A mapping between the `Location` enum
             and the corresponding nodes in the map.
    """

    _roads: RoadRegistry
    _root: Tree[Location]
    _locations: dict[Location, MapNode]

    def __init__(self, root: Location) -> None:
        """
        Initializes a Map object with `root` as the root location.

        Args:
            root (Location): The `Location` enum item of the primary
                point of focus of the map.
        """
        self._roads = SymmetricKeyDict[Location, float]()
        self._locations = dict[Location, MapNode]()
        self.register_location(location=root)
        self._root = self._locations[root]

    def register_location(self, location: Location) -> None:
        """
        Registers a location in the map.

        NOTE:
        Avoids duplicate entries by checking whether the location is
        already registed in the map.

        Args:
            location (Location): The `Location` enum item corresponding
                to the location to be registered.
        """
        if location not in self._locations:
            node: MapNode = Tree[Location](value=location)
            self._locations[location] = node

    @property
    def root(self) -> Tree[Location]:
        return self._root

    def add_road(self, loc_from: Location, loc_to: Location, fare: float) -> None:
        """
        Adds a road between two locations in the map.

        Parameters have `_from` and `_to` suffixes to indicate that the map
        is implemented as a *tree*. `loc_from` and `loc_to` must be such that
        the path `(root, loc_from, loc_to)` is present in the map's tree as
        decided by the user beforehand.

        Args:
            loc_from (Location): The location from which the road starts.
            loc_to (Location): The location to which the road goes.
        """
        self._locations[loc_from].add_child(child=self._locations[loc_to])
        self._roads[loc_from, loc_to] = fare

    def get_road_fare(self, loc_1: Location, loc_2: Location) -> float:
        """
        Gets the fare to go from `loc_1` to `loc_2` on the map. The ordering
        of the locations does not matter like `add_road`, as `self._roads`
        is implemented as a symmetric key dictionary.

        Args:
            loc_1 (Location): The `Location` at one end of the road.
            loc_2 (Location): The `Location` at the other end (LOL).
        """
        return self._roads[loc_1, loc_2]

    def show(self) -> None:
        self._root.show()

    def _find_route(self, loc_start: Location, loc_end: Location) -> list[Location]:
        """
        Finds a route between the two given locations in the map.

        Args:
            loc_start (Location): The source `Location` of the route.
            loc_end (Location): The destination `Location` of the route.

        Returns:
            list[Location]: The `list` of `Location`s indicating the different
                locations through which the route goes.
        """
        start = self._locations[loc_start]
        end = self._locations[loc_end]
        route: list[MapNode] = find_route(start=start, end=end)
        return [place.value for place in route]

    def get_fare_on_route(self, route: list[Location]) -> float:
        """
        Gets the fare born by travelling on a given `route`.

        Args:
            route (list[Location]): The route to calculate the travel
                fare on.

        Returns:
            float: The fare to travel on the given route.
        """
        return sum(
            [self._roads[loc_1, loc_2] for loc_1, loc_2 in zip(route[:-1], route[1:])]
        )

    def make_trip(
        self, loc_start: Location, loc_end: Location
    ) -> tuple[list[Location], float]:
        """
        Plans a trip from `loc_start` to `loc_end` and returns the route
        on the map tree and the fare born on that route.

        Args:
            loc_start (Location): The starting `Location` of the trip.
            loc_end (Location): The ending `Location` of the trip.

        Returns:
            tuple[list[Location], float]: Tuple of -
                - The route to be followed on the map.
                - The fare on that route.
        """
        route = self._find_route(loc_start=loc_start, loc_end=loc_end)
        fare = self.get_fare_on_route(route=route)
        return route, fare

    def get_passenger_route_fare(
        self, passenger: Passenger
    ) -> tuple[list[Location], float]:
        """
        Plans a trip for a given `Passenger`, and returns the route to travel
        on the map and the fare.

        Args:
            passenger (Passenger): The passenger to plan the trip for.

        Returns:
            tuple[list[Location], float]: Tuple of -
                - The route to be followed on the map.
                - The fare on that route.
        """
        return self.make_trip(loc_start=passenger.source, loc_end=passenger.destination)
