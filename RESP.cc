#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(32,16,2); // cria o display com o nome "lcd" no endereço 32
                                // com 16 colunas e 2 linhas NB: como Tipo va escolhido PCF8574

int buttonLeft;
int buttonRight;
int buttonConfirm;

const int BUTTON_LEFT_PIN = 2;
const int BUTTON_RIGHT_PIN = 3;
const int BUTTON_CONFIRM_PIN = 4;

// Opções de humor e sugestões
const char* humores[] = {"Feliz", "Triste", "Ansioso", "Calmo"};
const char* sugestoes[] = {
  "Continue sorrindo!",
  "Tente ouvir musica",
  "Respire fundo",
  "Aproveite a paz"
};
int totalHumores = 4;
int humorIndex = 0;
bool confirmado = false;

void setup() {
  lcd.init();         // inicializa o LCD
  lcd.backlight();    // ativa a retroiluminação
  lcd.setCursor(5, 0);// posiciona o cursor na 6a coluna e 1a linha
  lcd.print(";D R.E.S.P.");
  pinMode(BUTTON_LEFT_PIN, INPUT);
  pinMode(BUTTON_RIGHT_PIN, INPUT);
  pinMode(BUTTON_CONFIRM_PIN, INPUT);
  Serial.begin(9600);
  delay(2000);        // Delay para ver a mensagem inicial

  // Exibe a pergunta inicial no LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Como voce esta?");
  mostrarHumor(humores[humorIndex]);
}

void loop() {
  buttonLeft = digitalRead(BUTTON_LEFT_PIN);  // lê e memoriza o estado do botão da esquerda
  buttonRight = digitalRead(BUTTON_RIGHT_PIN); // lê e memoriza o estado do botão da direita
  buttonConfirm = digitalRead(BUTTON_CONFIRM_PIN); // lê e memoriza o estado do botão de confirmação

  // Verifica se o botão esquerdo foi pressionado
  if (buttonLeft == HIGH && !confirmado) {
    humorIndex = (humorIndex - 1 + totalHumores) % totalHumores;
    mostrarHumor(humores[humorIndex]);
    delay(300);  // Debounce
  }

  // Verifica se o botão direito foi pressionado
  if (buttonRight == HIGH && !confirmado) {
    humorIndex = (humorIndex + 1) % totalHumores;
    mostrarHumor(humores[humorIndex]);
    delay(300);  // Debounce
  }

  // Verifica se o botão de confirmação foi pressionado
  if (buttonConfirm == HIGH) {
    if (!confirmado) {
      confirmado = true;
      mostrarSugestao(sugestoes[humorIndex]);
    } else {
      confirmado = false;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Como voce esta?");
      mostrarHumor(humores[humorIndex]);
    }
    delay(300);  // Debounce
  }
}

void mostrarHumor(const char* humor) {
  lcd.setCursor(0, 1);
  lcd.print("                ");  // Limpa a linha
  lcd.setCursor(0, 1);
  lcd.print(humor);
}

void mostrarSugestao(const char* sugestao) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sugestao:");
  lcd.setCursor(0, 1);
  lcd.print(sugestao);
}
