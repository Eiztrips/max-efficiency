import {
  Panel,
  Grid,
  Container,
  Flex,
  Avatar,
  Typography,
  ToolButton,
  CellList,
  CellHeader,
  CellSimple,
  CellAction,
  Counter,
  CellInput,
  Switch,
  Button,
  IconButton,
} from "@maxhub/max-ui";
import "@maxhub/max-ui/dist/styles.css";

const App = () => (
  <Panel mode="secondary">
    <Flex direction="column" gap={24}>
      <Container>
        <Flex direction="column" align="center" gap={16}>
          <Avatar.Container size={96} rightBottomCorner={<Avatar.OnlineDot />}>
            <Avatar.Image
              fallback="ME"
              src={window.WebApp.initDataUnsafe.user.photo_url}
            />
          </Avatar.Container>

          <Flex direction="column" align="center">
            <Typography.Headline variant="large-strong">
              {window.WebApp.initDataUnsafe.user.first_name}{" "}
              {window.WebApp.initDataUnsafe.user.last_name}
            </Typography.Headline>
            <Typography.Body variant="small">1 подписчик</Typography.Body>
          </Flex>

          <Grid cols={4} gap={8}>
            <ToolButton onClick={() => {}}>Уведомл.</ToolButton>

            <ToolButton onClick={() => {}}>Поиск</ToolButton>

            <ToolButton onClick={() => {}}>Аудио</ToolButton>

            <ToolButton onClick={() => {}}>Еще</ToolButton>
          </Grid>
        </Flex>
      </Container>

      <Flex direction="column" gap={16}>
        <CellList mode="island" header={<CellHeader>О себе</CellHeader>}>
          <CellSimple height="compact" title="Frontend engineer 👨‍💻" />
        </CellList>

        <CellList mode="island" header={<CellHeader>Телефон</CellHeader>}>
          <CellAction height="compact" onClick={() => {}}>
            +8 888 888 88 88
          </CellAction>
        </CellList>

        <CellList mode="island">
          <CellSimple
            showChevron
            onClick={() => {}}
            title="Вложения"
            after={<Counter value={1245} rounded />}
            subtitle="Фото, видео, файлы и ссылки"
          />
        </CellList>
      </Flex>

      <CellList mode="island" header={<CellHeader>Настройки</CellHeader>}>
        <CellInput before="Статус" placeholder="Укажите статус" />

        <CellInput before="Страна" placeholder="Укажите страну" />

        <CellInput before="Город" placeholder="Укажите город" />

        <CellSimple
          as="label"
          title="Закрытый профиль"
          after={<Switch defaultChecked={false} />}
        />
      </CellList>

      <Container>
        <Flex gap={8}>
          <Button size="large" mode="secondary" appearance="neutral" stretched>
            Выйти
          </Button>

          <IconButton
            size="large"
            mode="secondary"
            appearance="neutral"
          ></IconButton>
        </Flex>
      </Container>
    </Flex>
  </Panel>
);

export default App;
