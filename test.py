from fuzzywuzzy import fuzz

a = "3304810->3304813->3304816->3304819->3304822->3304825->3304837->3304841->3304844->3304853->3304856->3304857->3304864->3304866->3304867->3304870->3304873->3304880->3304884->3304889->3304892->3304895->3304898->3304901->3304904->3304907->3304910->3304913->3304917->3304921->3304925->3304928->3304929->3304936->3304948->3304952->3304958->3303878->3303883->3303890->3304014->3304017->3302284->3302288->3302296->3302302->3302310->3302316->3302320->3302326->3302329->3302338->3302341->3302350->3302351->3302356->3302359->3302360->3293520->3293523->"
b = "3304810->3304813->3304816->3304819->3304822->3304825->3304837->3304841->3304844->3304853->3304856->3304857->3304864->3304866->3304867->3304870->3304873->3304880->3304884->3304889->3304892->3304895->3304898->3304901->3304904->3304907->3304910->3304913->3304917->3301987->3301994->3301996->3301997->3302002->3302005->3302008->3302011->3302014->3300422->3300427->3300430->3300654->3300656->3300686->3300713->3300717->3300722->3300725->3300729->3300744->3300252->3300255->3300258->3300261->3300264->3300267->3300270->3300273->3300276->3300285->"

print(fuzz.ratio(a, b))