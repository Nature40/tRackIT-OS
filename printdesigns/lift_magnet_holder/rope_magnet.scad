magnet_edge_length = 5.1;
rope_radius = 2.5;
wall_thickness = 1;
magnet_count = 4;

diff_padding = 1;


module rope_guard() {
    difference() {
        cylinder(r=rope_radius+wall_thickness, h=magnet_count*magnet_edge_length, $fs=0.1);
        translate([0,0,-wall_thickness])
            cylinder(r=rope_radius, h=magnet_count*magnet_edge_length + 2*wall_thickness, $fs=0.1);
    };
}

module magnet_guard() {
    outer_length = magnet_edge_length+2*wall_thickness;
    height = magnet_edge_length*magnet_count;
    diag_len = sqrt(outer_length*outer_length*2) / 2;
    
    union() {
        difference() {
            cube([outer_length, outer_length, height]);
            translate([wall_thickness, wall_thickness, -diff_padding])
            cube([magnet_edge_length, magnet_edge_length, height + 2*diff_padding]);
        }
        translate([outer_length/2, 0, height+magnet_edge_length-wall_thickness]) 
            rotate([0, 135, 0])
            union() {
                cube([diag_len, outer_length, wall_thickness]);
                cube([wall_thickness, outer_length, diag_len]);
            }
        
   }
    
}

union() {
    rope_guard();
    translate([-magnet_edge_length/2-wall_thickness, magnet_edge_length/2, 0])
        magnet_guard();
}
