import pygame
import cv2
import mediapipe as mp
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture-Controlled Car Game")

# Colors and Game Settings
WHITE = (255, 255, 255)
BLACK = (0,0,0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BG = (192,192,192)

CAR_WIDTH, CAR_HEIGHT = 50, 100
obstacle_speed = 5

score = 0
score_count = 0
level = 1
moving_side = ""

# Load Custom Font

font = pygame.font.Font("Tiny5-Regular.ttf", 40)

# Load Car Images
player_car_img = pygame.image.load("player_car.png")
player_car_img = pygame.transform.scale(player_car_img, (CAR_WIDTH, CAR_HEIGHT))
obstacle_car_img = pygame.image.load("obstacle_car.png")
obstacle_car_img = pygame.transform.scale(obstacle_car_img, (CAR_WIDTH, CAR_HEIGHT))
obstacle_car_img = pygame.transform.rotate(obstacle_car_img, 180)

# Car Position
car_x, car_y = WIDTH // 2, HEIGHT - 120

# OpenCV and Mediapipe Setup for Hand Detection
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Game Loop Variables
clock = pygame.time.Clock()
running = True
game_over = False
obstacles = []

# Helper Function to Spawn Obstacles
def spawn_obstacle():
    x_pos = random.randint(0, WIDTH - CAR_WIDTH)
    y_pos = -CAR_HEIGHT
    speed = random.randint(5, 10) + obstacle_speed
    obstacles.append([x_pos, y_pos, speed])

# Main Game Loop
while running:
    # PyGame Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_r:
            # Restart game if 'R' is pressed after game over
            game_over = False
            score = 0
            level = 1
            score_count = 0
            obstacle_speed = 5
            obstacles.clear()
            car_x = WIDTH // 2
            car_y = HEIGHT - 120

    if not game_over:
        # OpenCV Capture and Hand Detection
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a mirror view
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        # Steering Logic Based on Hand Position
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw landmarks on OpenCV frame for visualization
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                # Get the landmark for the index finger
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                x_position = int(index_finger_tip.x * WIDTH)

                # Move Car Based on Hand Position
                if x_position < WIDTH // 3:   # Left Side
                    car_x -= 10
                    moving_side = "Left <<"
                elif x_position > 2 * WIDTH // 3:   # Right Side
                    car_x += 10
                    moving_side = "Right >>"
                else:
                    moving_side = ""

        # Clamp car position to screen boundaries
        car_x = max(0, min(WIDTH - CAR_WIDTH, car_x))

        # Update Obstacles and Check for Collisions
        for obstacle in obstacles:
            obstacle[1] += obstacle[2]

            # Collision Detection
            if (car_x < obstacle[0] + CAR_WIDTH and
                car_x + CAR_WIDTH > obstacle[0] and
                car_y < obstacle[1] + CAR_HEIGHT and
                car_y + CAR_HEIGHT > obstacle[1]):
                game_over = True

            # Scoring: Increase score when obstacle passes the car
            if obstacle[1] > HEIGHT and not game_over:
                score += 1
                score_count += 1
                if score_count >= 10:
                    obstacle_speed += 1
                    level += 1
                    score_count = 0

        # Remove off-screen obstacles
        obstacles = [obstacle for obstacle in obstacles if obstacle[1] < HEIGHT]

        # Spawn New Obstacles
        if random.randint(0, 15) == 0:  # Adjust frequency
            spawn_obstacle()

        # Drawing Game Screen
        screen.fill(BG)
        screen.blit(player_car_img, (car_x, car_y))
        for obstacle in obstacles:
            screen.blit(obstacle_car_img, (obstacle[0], obstacle[1]))

        # Display Score and Level
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        level_text = font.render(f"Level : {level}", True, BLACK)
        screen.blit(level_text, (200, 10))

        movement_text = font.render(f"Moving : {moving_side}", True, RED)
        screen.blit(movement_text, (280, 560))

    else:
        # Game Over Screen
        screen.fill(BG)
        game_over_text = font.render("Game Over! Press 'R' to Restart", True, RED)
        score_text = font.render(f"Your Score: {score}", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()
    clock.tick(30)

    # Show the OpenCV Frame with Hand Tracking
    cv2.imshow("Hand Tracking", frame)

    # Quit if 'q' key is pressed in OpenCV window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False

# Cleanup
cap.release()
pygame.quit()
cv2.destroyAllWindows()
