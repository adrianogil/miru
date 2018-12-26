// Forward Declaration
class Transform;

class SceneObject
{
public:
    SceneObject();

    Transform* transform() const;

private:
    Transform* mTransform;
};