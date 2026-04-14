function sysCall_init()
    sim = require('sim')
    simROS2 = require('simROS2')

    robotHandle = sim.getObject('/PioneerP3DX')
    floor_handle = sim.getObject('/Floor')
    -- 1. Obtener handles de los motores
    leftMotor = sim.getObject('/PioneerP3DX/leftMotor')
    rightMotor = sim.getObject('/PioneerP3DX/rightMotor')

    -- 2. Definir los nombres de los publishers (Mantenlos consistentes)
    posePub = simROS2.createPublisher('/robot_pose', 'geometry_msgs/msg/Pose') -- Cambiado a Pose para simplificar
    clockPub = simROS2.createPublisher('/clock', 'rosgraph_msgs/msg/Clock')
    dimsPub = simROS2.createPublisher('/map_dims', 'std_msgs/msg/Float32MultiArray')
    -- OPCIONAL: Si vas a usar el láser, descomenta esto
    -- pub_scan = simROS2.createPublisher('/scan', 'sensor_msgs/msg/LaserScan')

    -- 3. Calcular dimensiones 
    local minX = sim.getObjectFloatParam(floor_handle, sim.objfloatparam_objbbox_min_x)
    local maxX = sim.getObjectFloatParam(floor_handle, sim.objfloatparam_objbbox_max_x)
    local minY = sim.getObjectFloatParam(floor_handle, sim.objfloatparam_objbbox_min_y)
    local maxY = sim.getObjectFloatParam(floor_handle, sim.objfloatparam_objbbox_max_y)

    floor_width = maxX - minX
    floor_height = maxY - minY
    origin_x = minX
    origin_y = minY

    -- Publicar dimensiones de una vez para que el nodo de Python sepa el tamaño
    simROS2.publish(dimsPub, {data = {floor_width, floor_height, origin_x, origin_y}})
    
    -- Suscribirse a los comandos de velocidad
    sub_vel = simROS2.createSubscription('/cmd_vel', 'geometry_msgs/msg/Twist', 'cmdVel_callback')
    -- Parámetros físicos del robot (aproximados para un Pioneer)
    wheel_track = 0.33  -- Distancia entre ruedas
    wheel_radius = 0.095 -- Radio de la rueda
end

function cmdVel_callback(msg)
    -- ROS2 envía: v (lineal x) y w (angular z)
    local v = msg.linear.x
    local w = msg.angular.z
    
    -- Convertir v y w a velocidad de cada rueda (Cinemática Diferencial)
    local v_left = v - (w * wheel_track / 2)
    local v_right = v + (w * wheel_track / 2)
    
    -- Convertir velocidad lineal de rueda a velocidad angular (rad/s) para el motor
    local omega_left = v_left / wheel_radius
    local omega_right = v_right / wheel_radius
    
    -- Aplicar a los motores
    sim.setJointTargetVelocity(leftMotor, omega_left)
    sim.setJointTargetVelocity(rightMotor, omega_right)
end

function sysCall_sensing()
    local pos = sim.getObjectPosition(robotHandle, -1)
    local quat = sim.getObjectQuaternion(robotHandle, -1)
    local t = sim.getSimulationTime()

    -- 1. Publicar Pose (Simplificado sin el Header para coincidir con el nodo Python anterior)
    simROS2.publish(posePub, {
        position = {x = pos[1], y = pos[2], z = pos[3]},
        orientation = {x = quat[1], y = quat[2], z = quat[3], w = quat[4]}
    })

    -- 2. Publicar Clock
    simROS2.publish(clockPub, {
        clock = {
            sec = math.floor(t),
            nanosec = math.floor((t % 1) * 1e9)
        }
    })
    
    -- 4. Publicar Láser (si el sensor existe)
    -- local result, data = sim.getCustomTableData(sensor_handle, 'laserData') 
    -- if result then simROS2.publish(pub_scan, data) end
end