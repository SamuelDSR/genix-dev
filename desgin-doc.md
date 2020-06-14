

# Manhuang

## World Design

### Map

- the whole world is formed by many hexagone tiles
- the size of each hexagone is ideally about 5-10 minutes walk for a player. Each hexagone is an independant unit, it has the following elements:
    * A **Genesis tower** which can be upgraded
    * A several different kinds of **terrain** which can generate different kinds of **basic resources**
    * Each player created is associated to a hexagone, a hexagone has a maximum number of players supported (100-1000) according to the levels of **genesis tower**
    * players can create/modify the hexagones under certain conditions and these changes could be seen by everyone
    * There are different kinds of hexgaones:
      * permanent: initial hexgaones created by the game, cannot be destroyed
      * new: hexagones created by players using a **genesis stone**, but isn't stable after being created. players must defend periodly attack from **monsters** outside. If the monsters manages to destory the **genesis tower**,  the whole hexagone will become unstable and will vanish after a period time.
      * neutre: hexagones without a **genesis tower** but still persists. There are no rule/order in these hexagones, also called **adventure park**
      * more to add
    * There are five classes of **genesis tower**: Metal, Wood, Water, Fire, Earth; some ressources will also have five attributes, the hexagone which ruled by a *Metal* will likely produce ressources with more *metal* attributes.


### Terrain
Different terrain can generate different precious ressources.
- Forest （森林）
- Grass （草原）
- Desert （沙漠）
- Moutain （山脉）
- Snow Moutain （雪山）
- Glacier （冰川）
- Plain （平原）
- Mire (沼泽)



### World resources and basic elements
- Veges: apple, banana, peach, pear, orange, melon, watermelon, grape, clementine, pineapple, strawberry, cherry, raspberry, backberry, coconuts, kiwi, lichee,  mango, olive, papaya, pomelo, pitaya, ...
- Fruits: bok-choy (小白菜), spinach(菠菜), cabbage (卷心菜), tomate, potato, daikon (白萝卜), carrot, eggplant, celery, broccoli (西兰花), onion, green mushroom, red mushroom, blue mushroom, pumpkin, corn, pepper, haricot, yellow bean, green bean, red been, black bean, Fennel(茴香), ginger, garlic(大蒜), Kohlrabi (甘蓝), ...
- Animals: pig, sheep/goat, cow, horse, goose, chicken, duck, cat,  different fishes, birds, snake, bear, tiger, lion, elephant, monkey, fog, crocodile
- Mines: gold, silver, iron, bronze, alimium, precious elements (Mg, Na, ...)
- Magic: metal gold, alive wood, heavy water, magic fire, soil (create magic things)
- water, air


## System Design

### Rules
- Different levels of genesis tower:  Stone(1-10), Bronze(10-30), Iron(30-70), Steam(70-100), Electrical(100-150), Silicon (150-200), Galaxy(200 - infinity)
- Level of genesis tower can impact of **reproduction rate** of ressources that can benefit everyone
- Each player must be associated to a genesis tower where it belongs (called home city),  farm ressources inside its own city pay less taxes
- The economic activities of players contribute to the level up of the genesis tower, include but not limited to:
  - Pay taxes by farmming ressources
  - Pay exchange taxes
  - Donate money
  - Defend enemy/monsters
  - Enforce rule/order
  - Construct buildings
- Players can purchuse/bid some lands (each hexagon is formed by many basic land) from **genesis tower**, then it can construct its own building on this land, any buildings on this land were marked by his ownership and therefore cannot be taken by other players unless expired.
- The one that create the **genesis tower** can mark his name+a small message on it.
- Players associated to the same city can elect a committe (several memebers) that is charged to manage this city: including 1. determine tax rate 2. land price 3. organise bidding 4. submit thinking/improvements to **genesis tower**, 5: determine level up path of **genesis tower**. 6: organize/cooridinate economic activities of all players 7: assure justicem 8: settle up disputes 9: vote to deprive the citizenship if (not active/contribute less) to allow new players 10: decide alliance with other hexagones
  .
- Player that is dead will spawn near the **genesis tower** in his city after a short period time
- A interim/temporary magic structure allow players to spawn here if constructed (at a high cost for a limited times)
- Law:
  - Player cannot hurt other players unless being attacked
  - Player attacks first will be guilty and any other players in this area can enforce law by attacking this people unless he is willing to turn himself/herself on (by pausing all its activity)
  - Player who commit a crime and manage to get escaped will have a bond, this bond will not disappear unless somebody (bondty hunter) kills him/her or he/she turn himself in.
  

- Trading systems
  - Players can sell/buy materials/product via market (has a tax)
  - Players can also meet in person and use a garantee box to make a deal
  - No official currency
  

## Content Design

#### Player

- Unique DNA (256 bits/1024 bits), each 16 bits determine a random hidden attribute of player
- No explicite player level, instead of, have skill levels + Five Elements Level + Player attribute + Age system
- No explicite player class systems,  player is differentiated by his choice of skill sets.
- Player attribute: HP/MaxHP, MP/MaxMP, Hunger, Five Elements Level, Different skill levels, Age
  - HP/MaxHP: increase slowly along with age (each birthday will give a gift to increase maxHP), can be temporaily increased using some Elixirs
  - MP/MaxHP: increase slowly along with age, same with HP, can be temporaily increased using some elixirs
  - Hunger: descreased along with times, increasing using food, five elements levels can be increased by eating the corresponding food, higher better or by stay in some corresponding area
  - Strength: determine the basic damage and defense
  - Five elements level:  **Metal**, **Wood**, **Water**, **Fire**, **Earth**,  and there are five corresponding skills sets, skill can only enforced/level up by 
    - Using that skills to kill monsters/enemys
    - Practicing in arena, if the opponent have a higher skill level than you, (A virtual AI will automatically generated) 
    - Each some elixirs (but at the cost of level up by the two previous ways)
    - Practing alone with Daocaoren (稻草人/练功桩)
- Armor systems
    - No armor level systems, but armor/equipement is classified into several ranking systems: (SS, S, A, B, C)
    - Attack weapons demands a minimum hp/mp/hunger or skill level of players
    - Defense weapons same with attack weapons
- Resistance to skills (player with main Metal ability will have more damage to players with main **wood** ability

- **Metal**:  reflect damage (反射伤害), forge (锻造，装备合成，修复)
- **Water**:  damage mitigation (减低伤害), frozen (冰冻),  减低攻击频率
- **Wood**:  damage convert to hp (伤害变生命), heel （治疗）， agriculture (培植丹药，植物)
- **Fire**: 加攻击(more damage), 炼丹
- **Earth**: MP 吸收， 催熟植物, 加防御光环


#### Damage control
damage = basic damange + armor damage
#### NPC

#### City NPC

#### Monsters

### Interaction system

### Trading and contract system


## Level Design

