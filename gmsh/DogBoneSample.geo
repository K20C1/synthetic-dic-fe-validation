SetFactory("OpenCASCADE");
Merge "DogBoneSample.step";
//+
Line(37) = {24, 6};
Line(38) = {22, 8};
Line(41) = {5, 23};
Line(42) = {7, 21};
Line(45) = {24, 23};
Line(46) = {6, 5};
Line(47) = {22, 21};
Line(48) = {8, 7};
Line(60) = {20, 10};
Line(61) = {10, 9};
Line(62) = {9, 19};
Line(63) = {19, 20};
Line(64) = {18, 12};
Line(65) = {12, 11};
Line(66) = {11, 17};
Line(67) = {17, 18};
//+
Curve Loop(201) = {37, 46, -41, -45};
Plane Surface(301) = {201};
Curve Loop(202) = {38, 48, -42, -47};
Plane Surface(302) = {202};
Curve Loop(203) = {60, 61, 62, 63};
Plane Surface(303) = {203};
Curve Loop(204) = {64, 65, 66, 67};
Plane Surface(304) = {204};
//+
BooleanFragments{ Volume{1}; Delete; }{ Surface{301, 302, 303, 304}; Delete; }
//+
// ---- Fillet arcs, both shoulders = 20 ----
Transfinite Curve {33, 34, 31, 29, 13, 15, 17, 18} = 20 Using Progression 1;
//+
// ---- Gauge block (Volume 3), length = 40 ----
Transfinite Curve {23, 27, 21, 24} = 40 Using Progression 1;
Transfinite Surface {302};
Transfinite Surface {303};
Transfinite Surface {314};
Transfinite Surface {315};
Transfinite Surface {316};
Transfinite Surface {317};
Transfinite Volume {3};
Recombine Surface {302, 303, 314, 315, 316, 317};
//+
// ---- Shared cross-section: width = 12, thickness = 4 everywhere ----
Transfinite Curve {38, 42, 30, 36, 11, 6, 1, 3, 28, 22, 14, 20} = 12 Using Progression 1;
Transfinite Curve {41, 43, 32, 35, 8, 12, 2, 4, 25, 26, 16, 19} = 4 Using Progression 1;
//+
// ---- Short grip (Volume 5), length = 15 ----
Transfinite Curve {44, 39, 40, 37} = 15 Using Progression 1;
Transfinite Surface {304};
Transfinite Surface {324};
Transfinite Surface {326};
Transfinite Surface {322};
Transfinite Surface {325};
Transfinite Surface {323};
Transfinite Volume {5};
Recombine Surface {304, 324, 326, 322, 325, 323};
//+
// ---- Long grip (Volume 1), length = 15 ----
Transfinite Curve {9, 7, 5, 10} = 15 Using Progression 1;
Transfinite Surface {301};
Transfinite Surface {305};
Transfinite Surface {308};
Transfinite Surface {306};
Transfinite Surface {307};
Transfinite Surface {309};
Transfinite Volume {1};
Recombine Surface {301, 305, 308, 306, 307, 309};
//+
// ---- Fillet block (Volume 2, left) ----
Transfinite Surface {310};
Transfinite Surface {311};
Transfinite Surface {312};
Transfinite Surface {313};
Transfinite Volume {2};
Recombine Surface {310, 311, 312, 313, 301, 302};
//+
// ---- Fillet block (Volume 4, right) ----
Transfinite Surface {318};
Transfinite Surface {319};
Transfinite Surface {320};
Transfinite Surface {321};
Transfinite Volume {4};
Recombine Surface {318, 319, 320, 321, 303, 304};
//+
// ---- Second-order elements ----
Mesh.ElementOrder = 2;
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 1;
//+
// ---- Export as Gmsh 2.2 for MOOSE ----
Mesh.MshFileVersion = 2.2;
//+
// ---- Physical groups for MOOSE ----
Physical Volume("specimen") = {1, 2, 3, 4, 5};
Physical Surface("grip_loaded") = {305};
Physical Surface("grip_fixed") = {324};
