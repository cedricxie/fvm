Point(1) = {0, 0, 0, 0.1};
Point(2) = {1, 0, 0, 0.1};
Point(3) = {4, 0, 0, 0.5};
Point(4) = {4, 4, 0, 1.0};
Point(5) = {0, 4, 0, 1.0};
Point(6) = {0, 1, 0, 0.1};
Circle(1) = {2,1,6};
Line(2) = {2,3};
Line(3) = {3,4};
Line(4) = {4,5};
Line(5) = {5,6};
Line Loop(6) = {1,-5,-4,-3,-2};
Plane Surface(7) = {6};
Physical Line(101) = {5};
Physical Line(102) = {2};
Physical Line(112) = {4};
Physical Line(200) = {1};
Physical Surface(11) = {-7};
