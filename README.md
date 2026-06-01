# graphNet

<p align="center">
  <a href="#english">English</a> •
  <a href="#русский">Русский</a>
</p>

---

<a name="english"></a>
# graphNet (English)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**graphNet** is a cross-platform desktop application designed for visual prototyping and construction of neural network architectures. Using an intuitive node-graph interface, users can create layers, link them to define the data flow, and configure parameters for each individual node.

---

## About the Project

Developing deep learning models often requires writing boilerplate code to define complex, multi-branch architectures. **graphNet** aims to simplify this process by providing a visual workspace where you can:
* **Assemble architectures interactively:** Add layers (nodes) such as Linear, Conv2D, Pooling, or Activation functions, and connect them with edges.
* **Configure hyperparameters:** Adjust weights, kernel sizes, strides, activation functions, and other layer parameters directly inside the GUI.
* **Visualize the flow:** Easily trace how data moves through complex topologies, including multi-input or multi-output systems.

### ️ Screenshots & Media

#### Main Workspace
![graphNet Workspace](Assets/preview.jpg)
*Figure 1: Visual workspace with nodes and connections representing a neural network.*

#### Video Demonstration
Below is a video demonstrating the workflow, from placing the first node to running the application:

<video src="Assets/demo.mp4" controls width="100%"></video>
---

## How to Run

You can run **graphNet** either as a standalone pre-compiled application or directly from the source code.

### Option 1. Run via Executable (.EXE)
This is the easiest way for Windows users who do not want to install Python or set up a command-line environment.

1. Go to the **Releases** section on the right side of this GitHub repository.
2. Download the latest `graphNet.zip` (or `graphNet.exe`) archive.
3. Extract the archive to any folder on your computer.
4. Double-click **`graphNet.exe`** to launch the application.

---

### Option 2. Run via Console (using `uv`)
If you want to run the project from source, it is highly recommended to use [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver.

#### 1. Install `uv`
* **Windows:**
  ```powershell
  winget install astral-sh.uv
  ```
* **macOS:**
  ```bash
  brew install uv
  ```
* **Linux:**
  ```bash
  pip install uv
  ```

#### 2. Run the application
Once `uv` is installed, navigate to the project directory and execute:
```bash
uv run main.py
```
*`uv` will automatically create a virtual environment, install the correct Python version, install all required dependencies listed in `pyproject.toml`, and launch the app.*

#### 3. Standard `pip` alternative (Optional)
If you prefer traditional tools:
```bash
pip install -r requirements.txt
python main.py
```

---

## ️ Building from Source (.EXE compilation)

If you want to compile your own `.exe` file after making changes to the source code, you can use one of these methods:

### Method A. Using `make`
If `make` is installed on your Windows environment:
```bash
make build
```
The compiled executable will be placed in the `dist/` folder.

### Method B. Interactive Build via `auto-py-to-exe`
1. Install the tool:
   ```bash
   pip install auto-py-to-exe
   ```
2. Launch it:
   ```bash
   auto-py-to-exe
   ```
3. Set the following options in the interface:
   * **Script Location:** Choose `main.py`.
   * **One File / One Directory:** Select *One File*.
   * **Console Window:** Select *Window Based (hide the console)*.
   * **Additional Files:** Click *Add Folder* and add the `Assets` folder (ensure the destination path is set to `Assets`).
4. Click **«Convert .py to .exe»**. The output file will be generated in the `output/` directory.

---

<a name="русский"></a>
# graphNet (Русский)

**graphNet** — это кроссплатформенное десктопное приложение на Python, разработанное для визуального проектирования и конструирования архитектур нейронных сетей. С помощью интерфейса в виде графа пользователи могут добавлять слои (узлы), связывать их для определения потока данных и настраивать параметры каждого элемента.

---

## О проекте

Проектирование архитектур глубокого обучения часто требует написания шаблонного кода, особенно для сложных сетей с ветвлением. **graphNet** призван решить эту проблему, предоставляя графическую рабочую область, где вы можете:
* **Интерактивно собирать архитектуру:** Добавлять слои (линейные, сверточные, пулинг, функции активации) и связывать их ребрами.
* **Конфигурировать параметры:** Настраивать размерности, шаги (stride), ядра свертки и другие параметры слоев напрямую через графический интерфейс.
* **Визуализировать потоки данных:** Наглядно видеть, как данные проходят через сложные топологии, включая системы с несколькими входами и выходами.

### Скриншоты и медиа-материалы

#### Главное рабочее пространство
![Рабочее пространство graphNet](Assets/preview.jpg)
*Рисунок 1: Визуальный редактор с нодами и связями, представляющими нейросеть.*

#### Видеодемонстрация работы
Ниже представлено видео, демонстрирующее процесс создания сети от первой ноды до запуска:

<video src="Assets/demo.mp4" controls width="100%"></video>
---

##  Как запустить

Вы можете запустить **graphNet** либо как готовую автономную программу, либо из исходного кода через консоль.

### Вариант 1. Запуск через готовый файл (.EXE)
Этот способ наиболее удобен для пользователей Windows, которым не требуется изменять код или настраивать окружение Python.

1. Перейдите в раздел **Releases** (Релизы) в правой части страницы этого репозитория.
2. Скачайте последнюю версию архива `graphNet.zip` (или файл `graphNet.exe`).
3. Распакуйте архив в любую удобную папку на компьютере.
4. Запустите файл **`graphNet.exe`** двойным кликом.

---

### Вариант 2. Запуск через консоль (с использованием `uv`)
Если вы хотите запустить проект из исходного кода, рекомендуется использовать [uv](https://github.com/astral-sh/uv) — быстрый инструмент для управления проектами на Python.

#### 1. Установите `uv`
* **Windows:**
  ```powershell
  winget install astral-sh.uv
  ```
* **macOS:**
  ```bash
  brew install uv
  ```
* **Linux:**
  ```bash
  pip install uv
  ```

#### 2. Запустите приложение
После установки `uv` перейдите в терминале в корневую директорию проекта и выполните команду:
```bash
uv run main.py
```
*`uv` автоматически создаст виртуальное окружение, загрузит необходимую версию Python, установит зависимости из файла `pyproject.toml` и запустит проект.*

#### 3. Альтернативный запуск через классический `pip`
Если вы предпочитаете стандартные инструменты:
```bash
pip install -r requirements.txt
python main.py
```

---

## Сборка исполняемого файла (.EXE из исходников)

Если вы внесли изменения в код и хотите собрать собственный `.exe` файл, воспользуйтесь одним из предложенных способов.

### Способ А. С использованием утилиты `make`
Если в вашей системе установлен инструмент `make`:
```bash
make build
```
Готовый исполняемый файл будет помещен в созданную папку `dist/`.

### Способ Б. Интерактивная сборка через `auto-py-to-exe`
1. Установите инструмент сборки:
   ```bash
   pip install auto-py-to-exe
   ```
2. Запустите графический интерфейс утилиты:
   ```bash
   auto-py-to-exe
   ```
3. Выполните настройки в открывшемся окне:
   * **Script Location:** Выберите ваш главный файл `main.py`.
   * **One File / One Directory:** Установите значение *One File*.
   * **Console Window:** Выберите *Window Based (hide the console)*.
   * **Additional Files:** Нажмите *Add Folder* и укажите папку `Assets` (убедитесь, что относительный путь назначения справа указан как `Assets`).
4. Нажмите синюю кнопку **«Convert .py to .exe»**. Собранное приложение будет сохранено в папке `output/`.
```